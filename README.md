This is the repository for the backend of my final qualifying work. 
The title of my work is "Monitoring the movement and functioning of agricultural machinery during field field work", 2024.
The backend has 11 functions necessary for communication between the mobile application and the database:
  - select_work (output of basic information about field work),
  - select_work_id (output ID of the field work just created by the operator),
  - select_works (displays a list of all field work),
  - select_start_form (output of information for creating field work),
  - select_user (to find a user in the database by username and password),
  - select_user_info (output user information),
  - insert_work (add field work to the database),
  - update_work (add the end time to the existing work in the database),
  - insert_work_parameter_values (add parameters of completed field work to the database),
  - insert_point (add geolocation of agricultural machinery to the database),
  - select_operator_works (check if the operator has unfinished field work).
--------------------------------------------------------------------------------------------------------------------------------------------------
Это репозиторий для серверной части моей выпускной квалификационной работы. 
Название моей работы - "Мониторинг перемещения и функционирования сельскохозяйственной техники в ходе выполнения полевых полевых работ", 2024 год.
В серверной части имеется 11 функций, необходимых для связи мобильного приложения и базы данных:
  - select_work (вывод основной информации о полевой работе),
  - select_work_id (вывод ID только что созданной оператором полевой работы),
  - select_works (вывод списка всех полевых работ),
  - select_start_form (вывод информации для создания полевой работы),
  - select_user (по логину и паролю найти пользователя в базе данных),
  - select_user_info (вывести информацию о пользователе),
  - insert_work (добавить в базу данных полевую работу),
  - update_work (добавить в существующую в базе данных работу время ее окончания),
  - insert_work_parameter_values (добавить в базу данных параметры завершенной полевой работы),
  - insert_point (добавить в базу данных геолокацию сельскохозяйственной техники),
  - select_operator_works (проверить наличие у оператора незавершенных им полевых работ).
  
