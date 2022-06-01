sqlite3 access-control.db "create table access (RFID integer, weekday text, start_time text, end_time text, primary key (RFID, weekday))"
sqlite3 access-control.db "create table log (RFID integer, date_time text, is_authorized integer, primary key (RFID, date_time))"
