# Northside Cultivation mushroom growing operational controls
 Automation for mushroom growing operations

The raspberry pi will collect sensor data regarding air temperature, relative humidity, and carbon dioxide content of the environment. Sampling will occur at at a frequency of 10 mHz, or once every 100 seconds. The pi will write the data to a mySQL database, which stores all of the samples for the last month. The raspberry pi will also serve as a host for a web server using Flask for the backend and hosted with NGINX, which can be connected to via external devices for monitoring of the enviroment(s). The web server will display realtime data from the sensors, as well as graphical data for monitoring of trends.

Along with providing data monitoring, the raspberry pi will serve as a controller for the systems that control humidity and airflow. Based on the information collected, it will actuate the misting system and/or change airflow via fan speed control in order to keep the environment(s) at optimal conditions for the growth of mushrooms.
