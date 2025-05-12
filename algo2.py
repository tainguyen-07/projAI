import heapq
import math
import random
from queue import deque
from collections import defaultdict
from typing import List, Tuple, Optional, Union, Dict, Set, Any

class Node:
    def __init__(self, hang: int, cot: int):
        self.hang = hang
        self.cot = cot

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.hang == other.hang and self.cot == other.cot

    def __hash__(self):
        return hash((self.hang, self.cot))

    def __repr__(self):
        return f"Node({self.hang}, {self.cot})"

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return (self.hang, self.cot) < (other.hang, other.cot)

    def khoangCach(self, nutKhac: 'Node') -> float:
        dx = abs(self.hang - nutKhac.hang)
        dy = abs(self.cot - nutKhac.cot)
        return math.hypot(dx, dy)

class Grid:
    def __init__(self, soHang: int, soCot: int, luoi: List[List[int]] = None):
        self.soHang = soHang
        self.soCot = soCot
        self.luoi = luoi if luoi else [[0 for _ in range(soCot)] for _ in range(soHang)]
        self.cacHuong = [
            (-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1)
        ]
        self.cacHuongKhongCheo = [
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]

    def hopLe(self, nut: Node) -> bool:
        return 0 <= nut.hang < self.soHang and 0 <= nut.cot < self.soCot and self.luoi[nut.hang][nut.cot] == 0

    def layLangGieng(self, nut: Node, baoGomCheo: bool = True) -> List[Tuple[Node, float]]:
        danhSachLangGieng = []
        cacHuong = self.cacHuong if baoGomCheo else [(dx, dy, 1) for dx, dy in self.cacHuongKhongCheo]
        for dx, dy, chiPhi in cacHuong:
            hangMoi, cotMoi = nut.hang + dx, nut.cot + dy
            nutLangGieng = Node(hangMoi, cotMoi)
            if self.hopLe(nutLangGieng):
                danhSachLangGieng.append((nutLangGieng, chiPhi))
        return danhSachLangGieng

    def layLangGiengKhongChiPhi(self, nut: Node, baoGomCheo: bool = True) -> List[Node]:
        danhSachLangGieng = []
        cacHuong = self.cacHuong if baoGomCheo else [(dx, dy, 1) for dx, dy in self.cacHuongKhongCheo]
        for dx, dy, _ in cacHuong:
            hangMoi, cotMoi = nut.hang + dx, nut.cot + dy
            nutLangGieng = Node(hangMoi, cotMoi)
            if self.hopLe(nutLangGieng):
                danhSachLangGieng.append(nutLangGieng)
        return danhSachLangGieng

class VanDe:
    def __init__(self, trangThaiBanDau: Node, trangThaiMucTieu: Node, luoi: Grid):
        self.trangThaiBanDau = trangThaiBanDau
        self.trangThaiMucTieu = trangThaiMucTieu
        self.luoi = luoi

    def kiemTraMucTieu(self, trangThai: Node) -> bool:
        return trangThai == self.trangThaiMucTieu

    def cacHanhDong(self, trangThai: Node) -> List[str]:
        cacHanhDongKhaThi = []
        cacHuong = [
            (-1, 0, "len"),
            (1, 0, "xuong"),
            (0, -1, "trai"),
            (0, 1, "phai")
        ]
        for dx, dy, tenHanhDong in cacHuong:
            hangMoi, cotMoi = trangThai.hang + dx, trangThai.cot + dy
            nutMoi = Node(hangMoi, cotMoi)
            if self.luoi.hopLe(nutMoi):
                cacHanhDongKhaThi.append(tenHanhDong)
        return cacHanhDongKhaThi

    def cacTrangThaiTiepTheo(self, trangThai: Node, hanhDong: str) -> List[Node]:
        cacHuong = {
            "len": (-1, 0),
            "xuong": (1, 0),
            "trai": (0, -1),
            "phai": (0, 1)
        }
        dx, dy = cacHuong[hanhDong]
        hangMoi, cotMoi = trangThai.hang + dx, trangThai.cot + dy
        trangThaiChinh = Node(hangMoi, cotMoi)
        if not self.luoi.hopLe(trangThaiChinh):
            return []

        ketQua = [trangThaiChinh]
        cacLangGieng = self.luoi.layLangGiengKhongChiPhi(trangThaiChinh)
        if cacLangGieng and random.random() < 0.3:
            trangThaiPhu = random.choice(cacLangGieng)
            ketQua.append(trangThaiPhu)
        return ketQua

def astar_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    hangDoi = []
    heapq.heappush(hangDoi, (diemBatDau.khoangCach(diemKetThuc), 0, diemBatDau))
    tuDauDen = {}
    diemG = {diemBatDau: 0}
    cacNutDaTham = []  # Stores (x, y, score)

    while hangDoi:
        _, chiPhiHienTai, nutHienTai = heapq.heappop(hangDoi)
        if any(n[0] == nutHienTai.hang and n[1] == nutHienTai.cot for n in cacNutDaTham):
            continue
        score = -1
        if nutHienTai in coins:
            score = 3
        elif nutHienTai == diemKetThuc:
            score = 100
        cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))
        if nutHienTai == diemKetThuc:
            duongDi = []
            nut = nutHienTai
            while nut in tuDauDen:
                duongDi.append(nut)
                nut = tuDauDen[nut]
            duongDi.append(diemBatDau)
            duongDi.reverse()
            yield duongDi, cacNutDaTham
            return

        for nutLangGieng, chiPhiDiChuyen in luoi.layLangGieng(nutHienTai):
            diemGtamThoi = chiPhiHienTai + chiPhiDiChuyen
            if diemGtamThoi < diemG.get(nutLangGieng, float('inf')):
                diemG[nutLangGieng] = diemGtamThoi
                diemF = diemGtamThoi + nutLangGieng.khoangCach(diemKetThuc)
                heapq.heappush(hangDoi, (diemF, diemGtamThoi, nutLangGieng))
                tuDauDen[nutLangGieng] = nutHienTai
        yield [], cacNutDaTham

    yield [], cacNutDaTham

def bfs_search_withAnimation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    hangDoi = deque([diemBatDau])
    tuDauDen = {diemBatDau: None}
    cacNutDaTham = [(diemBatDau.hang, diemBatDau.cot, -1)]

    while hangDoi:
        nutHienTai = hangDoi.popleft()
        if nutHienTai == diemKetThuc:
            duongDi = []
            nut = nutHienTai
            while nut is not None:
                duongDi.append(nut)
                nut = tuDauDen[nut]
            duongDi.reverse()
            cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, 100))
            yield duongDi, cacNutDaTham
            return

        for nutLangGieng in luoi.layLangGiengKhongChiPhi(nutHienTai):
            if nutLangGieng not in tuDauDen:
                tuDauDen[nutLangGieng] = nutHienTai
                hangDoi.append(nutLangGieng)
                score = 3 if nutLangGieng in coins else -1
                cacNutDaTham.append((nutLangGieng.hang, nutLangGieng.cot, score))
        yield [], cacNutDaTham

    yield [], cacNutDaTham

def lrta_star_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    giaTriH = defaultdict(lambda: float('inf'))
    giaTriH[diemBatDau] = diemBatDau.khoangCach(diemKetThuc)
    hangDoi = []
    heapq.heappush(hangDoi, (giaTriH[diemBatDau], 0, diemBatDau))
    tuDauDen = {diemBatDau: None}
    cacNutDaTham = [(diemBatDau.hang, diemBatDau.cot, -1)]
    chiPhiDenNut = {diemBatDau: 0}

    while hangDoi:
        _, chiPhiHienTai, nutHienTai = heapq.heappop(hangDoi)
        if chiPhiHienTai > chiPhiDenNut.get(nutHienTai, float('inf')):
            continue
        if not any(n[0] == nutHienTai.hang and n[1] == nutHienTai.cot for n in cacNutDaTham):
            score = 3 if nutHienTai in coins else -1
            if nutHienTai == diemKetThuc:
                score = 100
            cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))
        if nutHienTai == diemKetThuc:
            duongDi = []
            nut = nutHienTai
            while nut is not None:
                duongDi.append(nut)
                nut = tuDauDen.get(nut)
            duongDi.reverse()
            yield duongDi, cacNutDaTham
            return

        ungVien = []
        for nutLangGieng, chiPhi in luoi.layLangGieng(nutHienTai, baoGomCheo=False):
            chiPhiMoi = chiPhiHienTai + chiPhi
            if chiPhiMoi < chiPhiDenNut.get(nutLangGieng, float('inf')):
                chiPhiDenNut[nutLangGieng] = chiPhiMoi
                tuDauDen[nutLangGieng] = nutHienTai
                if nutLangGieng not in giaTriH:
                    giaTriH[nutLangGieng] = nutLangGieng.khoangCach(diemKetThuc)
                f = chiPhiMoi + giaTriH[nutLangGieng]
                heapq.heappush(hangDoi, (f, chiPhiMoi, nutLangGieng))
                ungVien.append((f, chiPhi, nutLangGieng))

        if ungVien:
            giaTriFmin = min(f for f, _, _ in ungVien)
            giaTriH[nutHienTai] = giaTriFmin - chiPhiHienTai
        else:
            giaTriH[nutHienTai] = float('inf')
        yield [], cacNutDaTham

    yield [], cacNutDaTham

def online_dfs_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    vanDe = VanDe(diemBatDau, diemKetThuc, luoi)
    nutHienTai = diemBatDau
    duongDiHienTai = [diemBatDau]
    cacNutDaTham = [(diemBatDau.hang, diemBatDau.cot, -1)]
    daTham = {diemBatDau}
    nganXep = []
    cacHanhDongDaThucHien = defaultdict(list)

    while True:
        if vanDe.kiemTraMucTieu(nutHienTai):
            cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, 100))
            yield duongDiHienTai, cacNutDaTham
            return

        cacHanhDong = vanDe.cacHanhDong(nutHienTai)
        cacHanhDongChuaThu = [hanhDong for hanhDong in cacHanhDong if hanhDong not in cacHanhDongDaThucHien[nutHienTai]]

        if cacHanhDongChuaThu:
            cacHanhDongUuTien = ["phai", "xuong", "trai", "len"]
            hanhDong = next((hd for hd in cacHanhDongUuTien if hd in cacHanhDongChuaThu), cacHanhDongChuaThu[0])
            cacHanhDongDaThucHien[nutHienTai].append(hanhDong)
            trangThaiKeTiep = vanDe.cacTrangThaiTiepTheo(nutHienTai, hanhDong)[0]
            nganXep.append((nutHienTai, duongDiHienTai[:], cacHanhDongDaThucHien[nutHienTai][:]))
            nutHienTai = trangThaiKeTiep
            duongDiHienTai = duongDiHienTai + [nutHienTai]
            if nutHienTai not in daTham:
                score = 3 if nutHienTai in coins else -1
                cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))
            daTham.add(nutHienTai)
        else:
            if not nganXep:
                yield [], cacNutDaTham
                return
            nutHienTai, duongDiHienTai, cacHanhDongDaThucHien[nutHienTai] = nganXep.pop()
            if nutHienTai not in daTham:
                score = 3 if nutHienTai in coins else -1
                cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))
        yield [], cacNutDaTham

def dijkstra_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    hangDoi = []
    heapq.heappush(hangDoi, (0, diemBatDau))
    tuDauDen = {diemBatDau: None}  # Sửa: Khởi tạo với None cho nút bắt đầu
    chiPhi = {diemBatDau: 0}
    cacNutDaTham = []  # Sửa: Bỏ nút bắt đầu khỏi cacNutDaTham ban đầu

    while hangDoi:
        chiPhiHienTai, nutHienTai = heapq.heappop(hangDoi)

        # Kiểm tra đã thăm
        if any(n[0] == nutHienTai.hang and n[1] == nutHienTai.cot for n in cacNutDaTham):
            continue

        # Tính điểm số và thêm vào cacNutDaTham
        score = -1
        if nutHienTai in coins:
            score = 3
        elif nutHienTai == diemKetThuc:
            score = 100
        cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))

        # Kiểm tra đích
        if nutHienTai == diemKetThuc:
            duongDi = []
            nut = nutHienTai
            while nut in tuDauDen and tuDauDen[nut] is not None:  # Sửa: Thêm kiểm tra None
                duongDi.append(nut)
                nut = tuDauDen[nut]
            duongDi.append(diemBatDau)  # Thêm nút bắt đầu
            duongDi.reverse()
            yield duongDi, cacNutDaTham
            return

        # Duyệt các nút kề
        for nutLangGieng, chiPhiDiChuyen in luoi.layLangGieng(nutHienTai, baoGomCheo=False):
            chiPhiMoi = chiPhiHienTai + chiPhiDiChuyen

            if chiPhiMoi < chiPhi.get(nutLangGieng, float('inf')):
                chiPhi[nutLangGieng] = chiPhiMoi
                tuDauDen[nutLangGieng] = nutHienTai
                heapq.heappush(hangDoi, (chiPhiMoi, nutLangGieng))

        yield [], cacNutDaTham

    yield [], cacNutDaTham  # Trường hợp không tìm thấy đường đi

def binary_backtracking_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    cacNutDaTham = [(diemBatDau.hang, diemBatDau.cot, -1)]
    duongDi = [diemBatDau]
    daTham = {diemBatDau}

    def quayLui(nutHienTai: Node, duongDiHienTai: List[Node]):
        score = 3 if nutHienTai in coins else -1
        if nutHienTai == diemKetThuc:
            score = 100
        cacNutDaTham.append((nutHienTai.hang, nutHienTai.cot, score))
        yield [], cacNutDaTham

        if nutHienTai == diemKetThuc:
            return duongDiHienTai

        cacHuongUuTien = [(0, 1), (1, 0)]
        cacHuongPhu = [(-1, 0), (0, -1)]
        for dx, dy in cacHuongUuTien + cacHuongPhu:
            hangMoi, cotMoi = nutHienTai.hang + dx, nutHienTai.cot + dy
            nutKeTiep = Node(hangMoi, cotMoi)
            if luoi.hopLe(nutKeTiep) and nutKeTiep not in daTham:
                daTham.add(nutKeTiep)
                ketQua = yield from quayLui(nutKeTiep, duongDiHienTai + [nutKeTiep])
                if ketQua:
                    return ketQua
        return None

    ketQua = yield from quayLui(diemBatDau, duongDi)
    if ketQua:
        cacNutDaTham.append((diemKetThuc.hang, diemKetThuc.cot, 100))
        yield ketQua, cacNutDaTham
    else:
        yield [], cacNutDaTham

def bidirectional_search_with_animation(luoi: Grid, diemBatDau: Node, diemKetThuc: Node, coins: Set[Node]):
    hangDoiTien = deque([diemBatDau])
    hangDoiLui = deque([diemKetThuc])
    tuDauDenTien = {diemBatDau: None}
    tuDauDenLui = {diemKetThuc: None}
    daThamTien = {diemBatDau}
    daThamLui = {diemKetThuc}
    cacNutDaTham = [(diemBatDau.hang, diemBatDau.cot, -1), (diemKetThuc.hang, diemKetThuc.cot, 100)]

    while hangDoiTien and hangDoiLui:
        nutHienTaiTien = hangDoiTien.popleft()
        for nutLangGieng in luoi.layLangGiengKhongChiPhi(nutHienTaiTien, baoGomCheo=False):
            if nutLangGieng not in daThamTien:
                daThamTien.add(nutLangGieng)
                tuDauDenTien[nutLangGieng] = nutHienTaiTien
                hangDoiTien.append(nutLangGieng)
                score = 3 if nutLangGieng in coins else -1
                if not any(n[0] == nutLangGieng.hang and n[1] == nutLangGieng.cot for n in cacNutDaTham):
                    cacNutDaTham.append((nutLangGieng.hang, nutHienTaiTien.cot, score))
                if nutLangGieng in daThamLui:
                    duongDi = []
                    nut = nutLangGieng
                    while nut is not None:
                        duongDi.append(nut)
                        nut = tuDauDenTien.get(nut)
                    duongDi.reverse()
                    nut = tuDauDenLui.get(nutLangGieng)
                    while nut is not None:
                        duongDi.append(nut)
                        nut = tuDauDenLui.get(nut)
                    yield duongDi, cacNutDaTham
                    return
        yield [], cacNutDaTham

        nutHienTaiLui = hangDoiLui.popleft()
        for nutLangGieng in luoi.layLangGiengKhongChiPhi(nutHienTaiLui, baoGomCheo=False):
            if nutLangGieng not in daThamLui:
                daThamLui.add(nutLangGieng)
                tuDauDenLui[nutLangGieng] = nutHienTaiLui
                hangDoiLui.append(nutLangGieng)
                score = 3 if nutLangGieng in coins else -1
                if not any(n[0] == nutLangGieng.hang and n[1] == nutLangGieng.cot for n in cacNutDaTham):
                    cacNutDaTham.append((nutLangGieng.hang, nutHienTaiLui.cot, score))
                if nutLangGieng in daThamTien:
                    duongDi = []
                    nut = nutLangGieng
                    while nut is not None:
                        duongDi.append(nut)
                        nut = tuDauDenTien.get(nut)
                    duongDi.reverse()
                    nut = tuDauDenLui.get(nutLangGieng)
                    while nut is not None:
                        duongDi.append(nut)
                        nut = tuDauDenLui.get(nut)
                    yield duongDi, cacNutDaTham
                    return
        yield [], cacNutDaTham

    yield [], cacNutDaTham

def find_highest_score_path(grid: Grid, start: Node, goal: Node, coins: Set[Node], visited_nodes: List[Tuple[int, int, int]] = None) -> List[Node]:
    """
    Find the path with the highest score using A* with score-based heuristic.
    Scoring: normal cell (-1), coin (+3), goal (+100), walls (impassable).
    Restrict to visited nodes if provided.
    """
    # Nếu có visited_nodes, tạo lưới mới chỉ chứa các ô đã thăm
    if visited_nodes:
        explored_grid = [[1 for _ in range(grid.soCot)] for _ in range(grid.soHang)]
        for x, y, _ in visited_nodes:
            explored_grid[x][y] = 0
        grid = Grid(grid.soHang, grid.soCot, explored_grid)

    def heuristic(node: Node, remaining_coins: Set[Node]) -> float:
        """Ước lượng điểm số tối đa từ node đến goal."""
        dist_to_goal = abs(node.hang - goal.hang) + abs(node.cot - goal.cot)
        # Ước lượng số coin có thể thu thập dựa trên khoảng cách
        coin_score = 0
        steps = dist_to_goal
        for coin in remaining_coins:
            dist_to_coin = abs(node.hang - coin.hang) + abs(node.cot - coin.cot)
            if dist_to_coin <= steps:
                coin_score += 3
                steps -= dist_to_coin
        # Điểm số tối đa: coin + đích - ô thường
        return coin_score + 100 - (dist_to_goal - len(remaining_coins))

    # Hàng đợi ưu tiên: (-f_score, g_score, node, collected_coins, path)
    pq = [(-heuristic(start, coins), 0, start, frozenset(), [start])]
    visited = set()  # Lưu trạng thái (node, collected_coins)
    came_from = {}   # Lưu đường đi: (node, collected_coins) -> (prev_node, prev_coins)

    while pq:
        f_score, g_score, current, collected, path = heapq.heappop(pq)
        state = (current, collected)
        if state in visited:
            continue
        visited.add(state)

        if current == goal:
            return path

        for neighbor, _ in grid.layLangGieng(current, baoGomCheo=False):
            new_g_score = g_score
            new_collected = set(collected)
            if neighbor in coins and neighbor not in collected:
                new_g_score += 3
                new_collected.add(neighbor)
            elif neighbor == goal:
                new_g_score += 100
            else:
                new_g_score -= 1

            new_state = (neighbor, frozenset(new_collected))
            if new_state not in visited:
                new_path = path + [neighbor]
                h_score = heuristic(neighbor, coins - new_collected)
                heapq.heappush(pq, (-(new_g_score + h_score), new_g_score, neighbor, frozenset(new_collected), new_path))
                came_from[new_state] = (current, collected)

    return []  # Không tìm được đường