import math
import random

#Tính khoảng cách Euclid giữa hai thành phố
def distance(a, b): 
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

#Tính tổng quãng đường của một tour (chu trình đóng)
def compute_energy(tour, cities):
    total = 0
    for i in range(len(tour)):
        city_a = cities[tour[i]]
        city_b = cities[tour[(i + 1) % len(tour)]]
        total += distance(city_a, city_b)
    return total

#Tạo nghiệm láng giềng ngẫu nhiên bằng cách hoán đổi vị trí của hai thành phố trong tour
def two_opt_move(tour, cities):
    n = len(tour)
    #Chọn hai chỉ số i, j ngẫu nhiên sao cho i < j
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n - 1)

    # TRƯỜNG HỢP ĐẶC BIỆT: đảo toàn bộ tour -> năng lượng không đổi
    if i == 0 and j == n - 1:
        new_tour = list(reversed(tour))
        return new_tour, 0.0

    a = tour[i - 1] if i > 0 else tour[-1]
    b = tour[i]
    c = tour[j]
    d = tour[j + 1] if j < n - 1 else tour[0]

    old_edges = distance(cities[a], cities[b]) + distance(cities[c], cities[d])
    new_edges = distance(cities[a], cities[c]) + distance(cities[b], cities[d])
    delta_e = new_edges - old_edges

    new_tour = tour[:]
    new_tour[i:j+1] = reversed(new_tour[i:j+1]) #đảo đoạn từ i đến j

    return new_tour, delta_e



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
