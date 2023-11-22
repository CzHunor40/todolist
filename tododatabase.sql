CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    task VARCHAR(255),
    points INT,
    completed BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (username, password) VALUES
('Kyra', 'password1'),
('Hunor', 'password2');

INSERT INTO tasks (user_id, task, points, completed) VALUES
(1, 'Task 1', 10, 0),
(1, 'Task 2', 5, 0),
(1, 'Task 2', 5, 0),
(2, 'Task 3', 8, 1),
(2, 'Task 4', 4, 0);