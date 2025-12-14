import math
import random

#Hàm tính khoảng cách Euclid giữa hai thành phố a và b
def distance(a, b): 
    # Công thức: sqrt((x2-x1)^2 + (y2-y1)^2)
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

#Hàm tính tổng quãng đường của toàn bộ lộ trình (TSP Distance)
def compute_tsp_distance(tour, cities):
    total = 0
    n = len(tour)
    for i in range(n):
        city_a = cities[tour[i]]
        # tour[(i + 1) % n] giúp nối thành phố cuối cùng về lại thành phố đầu tiên
        city_b = cities[tour[(i + 1) % n]]
        total += distance(city_a, city_b)
    return total

#Tạo nghiệm láng giềng ngẫu nhiên bằng cách hoán đổi vị trí của hai thành phố trong tour
def get_neighbor(tour, cities):
    n = len(tour)
    # Chọn ngẫu nhiên hai vị trí i và j để thực hiện đảo đoạn
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n - 1)

    # Tính toán chênh lệch khoảng cách (delta_e) thay vì tính lại từ đầu
    a = tour[i - 1] if i > 0 else tour[-1]
    b = tour[i]
    c = tour[j]
    d = tour[j + 1] if j < n - 1 else tour[0]

    # Hiệu số giữa các cạnh mới (a-c, b-d) và các cạnh cũ (a-b, c-d)
    old_edges = distance(cities[a], cities[b]) + distance(cities[c], cities[d])
    new_edges = distance(cities[a], cities[c]) + distance(cities[b], cities[d])
    delta_e = new_edges - old_edges

    # Tạo nghiệm láng giềng bằng cách đảo ngược đoạn từ i đến j
    neighbor_tour = tour[:]
    neighbor_tour[i:j+1] = reversed(neighbor_tour[i:j+1])

    return neighbor_tour, delta_e



#Tự động ước lượng nhiệt độ ban đầu sao cho xác suất chấp nhận nghiệm xấu phù hợp với bài toán
def estimate_initial_temperature(cities, sample_size=200):
    n = len(cities)
    base = list(range(n)) #tạo một tour cơ sở
    random.shuffle(base)

    deltas = []
    for _ in range(sample_size):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)

        # ước lượng ΔE khi random 2-opt
        a = base[i - 1] if i > 0 else base[-1]
        b = base[i]
        c = base[j]
        d = base[(j + 1) % n]

        old_edges = distance(cities[a], cities[b]) + distance(cities[c], cities[d])
        new_edges = distance(cities[a], cities[c]) + distance(cities[b], cities[d])
        delta = new_edges - old_edges

        if delta > 0:
            deltas.append(delta)


    if len(deltas) == 0:
        return 10  

    avg_delta = sum(deltas) / len(deltas)
    T_initial = -avg_delta / math.log(0.9)   
    return T_initial


#Uớc lượng nhiệt độ dừng sao cho thuật toán có thể hội tụ
def estimate_T_min(cities):
    distances = []
    for i in range(len(cities)): #tính khoảng cách giữa tất cả các cặp thành phố
        for j in range(i + 1, len(cities)):
            distances.append(distance(cities[i], cities[j]))

    avg_dist = sum(distances) / len(distances) #tính khoảng cách trung bình
    return avg_dist * 1e-3

#Điều chỉnh hệ số làm mát dựa trên tỷ lệ chấp nhận nghiệm mới
def adaptive_alpha(acceptance_rate):
    if acceptance_rate > 0.8:
        return 0.98
    elif acceptance_rate < 0.2:
        return 0.999
    return 0.995


def simulated_annealing(cities, max_iter=150000, log=False):

    n = len(cities)

   
    T_initial = estimate_initial_temperature(cities)
    if T_initial < 1e-6:
        T_initial = 1.0
    T_min = estimate_T_min(cities)
    T = T_initial

    #Khởi tạo current ngẫu nhiên
    current = list(range(n))
    random.shuffle(current)
    current_energy = compute_energy(current, cities)

    best = current[:]
    best_energy = current_energy
    #Thống kê số nghiệm được chấp nhận
    accepted = 0
    attempted = 0

    for step in range(max_iter):

        attempted += 1

       
        new, dE = two_opt_move(current, cities)

        
        if dE < 0:
            current = new
            current_energy += dE
            accepted += 1

        else:
            
            P = math.exp(-dE / T)
            if random.random() < P:
                current = new
                current_energy += dE
                accepted += 1

       
        if current_energy < best_energy:
            best = current[:]
            best_energy = current_energy

        
        if step % 5000 == 0 and attempted > 0:
            rate = accepted / attempted
            alpha = adaptive_alpha(rate)
            T = T * alpha
            accepted = attempted = 0

        
        if T < T_min:
            break

    if log:
        print("T_initial:", T_initial)
        print("T_min:", T_min)

    return best, best_energy
if __name__ == "__main__":
    random.seed(1000)
    cities = [(random.randint(0,100), random.randint(0,100)) for _ in range(8)]
    best, dist = simulated_annealing(cities, max_iter=20000, log=True)
    print("Best tour:", best)
    print("Distance:", dist)
