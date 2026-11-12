#!/usr/bin/env bash
# Демонстрація REST API (пункт 7). Сервер: uv run uvicorn lab4.main:app --reload
API=${API:-http://localhost:8000/api}
J='-H Content-Type:application/json'
step() { printf '\n### %s\n' "$*"; }
run()  { printf '$ %s\n' "$*"; eval "$@"; printf '\n'; }

step "GET список (2 записи)"
run "curl -s '$API/instruments?limit=2'"

step "GET окремий запис"
run "curl -s $API/musicians/1"

step "POST створення інструмента"
run "curl -s -i $J -X POST $API/instruments -d '{\"serial_number\":\"ymh-555777\",\"name\":\"Pacifica 612V\",\"category_id\":1,\"manufacturer_id\":1,\"price\":899.99,\"year_made\":2024}' | grep -iE 'HTTP|location|^\{'"

step "PUT оновлення"
ID=$(curl -s "$API/instruments?limit=200" | python3 -c 'import sys,json; print(json.load(sys.stdin)[-1]["id"])')
run "curl -s $J -X PUT $API/instruments/$ID -d '{\"serial_number\":\"YMH-555777\",\"name\":\"Pacifica 612VIIX\",\"category_id\":1,\"manufacturer_id\":1,\"price\":949.00,\"year_made\":2024}'"

step "Перевірка, що дані в БД (psql)"
run "psql -h localhost -U postgres -c \"SELECT id, serial_number, name, price FROM instruments WHERE id = $ID\""

step "DELETE"
run "curl -s -o /dev/null -w 'HTTP %{http_code}' -X DELETE $API/instruments/$ID"
run "curl -s -w ' HTTP %{http_code}' $API/instruments/$ID"

step "Regex-валідація: поганий email і телефон -> 422"
run "curl -s -w ' HTTP %{http_code}' $J -X POST $API/musicians -d '{\"full_name\":\"Тест Тестович\",\"email\":\"not-an-email\",\"phone\":\"0501234567\"}'"

step "Regex-валідація: поганий серійний номер -> 422"
run "curl -s -w ' HTTP %{http_code}' $J -X POST $API/instruments -d '{\"serial_number\":\"12345\",\"name\":\"X\",\"category_id\":1,\"manufacturer_id\":1,\"price\":1,\"year_made\":2020}'"

step "Коректний музикант -> 201"
run "curl -s -w ' HTTP %{http_code}' $J -X POST $API/musicians -d '{\"full_name\":\"Роман Теплухін\",\"email\":\"roman.t@music.ua\",\"phone\":\"+380 95 1234567\"}'"

step "1:N — інструменти виробника (Korg)"
run "curl -s $API/manufacturers/9/instruments | python3 -c 'import sys,json; [print(i[\"serial_number\"], i[\"name\"]) for i in json.load(sys.stdin)]'"

step "N:M — інструменти музиканта, прив'язка та відв'язка"
run "curl -s $API/musicians/1/instruments | python3 -c 'import sys,json; [print(i[\"id\"], i[\"name\"], i[\"since_year\"]) for i in json.load(sys.stdin)]'"
run "curl -s -w ' HTTP %{http_code}' $J -X POST $API/musicians/1/instruments/37 -d '{\"since_year\":2020}'"
run "curl -s -o /dev/null -w 'HTTP %{http_code}' -X DELETE $API/musicians/1/instruments/37"

step "Неіснуючий запис -> 404"
run "curl -s -w ' HTTP %{http_code}' $API/categories/999"
