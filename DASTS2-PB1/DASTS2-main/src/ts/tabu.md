# Tabu

> move01: (khách hàng, index chuyển đến) 

 chuyển 1 khách hàng sang thành trip mới của drone, hoặc vào 1 nhân viên có hành trình trống. index sẽ là 2 giá trị nếu chuyển thành trip mới của drone, 1 giá trị nếu chuyển vào hành trình của nhân viên.

> move10: (khách hàng 1, khách hàng 2)

chuyển khách hàng 1 ra sau khách hàng 2

> move11: (khách hàng 1, khách hàng 2)

hoán đổi vị trí khách hàng 1 và 2

> move20: (khách hàng 1, khách hàng 2, khách hàng 3)

khách hàng 1 và 2 liền nhau, di chuyển ra sau khách hàng 3

> move21: (khách hàng 1, khách hàng 2, khách hàng 3)

khách hàng 1 và 2 liền nhau, hoán đổi vị trí cho khách hàng 3

> move2opt: (khách hàng 1, khách hàng 2, khách hàng 3, khách hàng 4)

khách hàng 1,2 cùng trip, kề nhau , 3,4 cùng trip kề nhau, hoán đổi phần 2 phần trip được chia ra bởi các khách hàng cho nhau


# Khởi tạo lời giải
> Cách 1:
	Chọn lần lượt các nút xa nhất cho từng phương tiện.
	từ các nút khởi đầu đó, thực hiện tham lam, chọn nút gần nhất với nút cuối hành trình hiện tại.
	nếu mà quá thời gian chờ thì ngắt, nhân viên thì dừng, drone thì đi trip mới

> Cách 2:
Tương tự như cách 1 nhưng chọn nút khởi đầu là nút gần nhất

> Cách 3:
Thực hiện quét theo tia từ nút xa (gần) nhất cho đến khi bị vượt quá thời gian chờ thì ngắt. 
TIếp tục thực hiện quét như thế cho từng trip của drone, lần lượt từng drone 1. (trip1 d1, trip1 d2, trip2 d1, trip2 d2…) trip gần nhất drone nào về sớm hơn thì ưu tiên tạo trip mới cho nó trước.
Quét ngược hoặc xuôi theo chiều kim đồng hồ (random từ đầu).


Sinh cả 3 cách, rồi chọn cái nào tốt nhất.
