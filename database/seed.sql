
USE civic_connect;

INSERT IGNORE INTO departments (name, description) VALUES
('Sanitation', 'Waste collection and cleanliness services'),
('Roads and Infrastructure', 'Road maintenance and public infrastructure'),
('Water Supply', 'Water supply and drainage complaints'),
('Electricity', 'Street lighting and electrical infrastructure'),
('Public Safety', 'Public safety and civic hazard reports');

INSERT INTO resources
    (department_id, name, resource_type, quantity, available_quantity)
SELECT id, 'Maintenance Vehicle', 'Vehicle', 5, 5
FROM departments
WHERE name = 'Roads and Infrastructure'
AND NOT EXISTS (
    SELECT 1 FROM resources
    WHERE name = 'Maintenance Vehicle'
      AND department_id = departments.id
);

INSERT INTO resources
    (department_id, name, resource_type, quantity, available_quantity)
SELECT id, 'Sanitation Team', 'Staff Team', 4, 4
FROM departments
WHERE name = 'Sanitation'
AND NOT EXISTS (
    SELECT 1 FROM resources
    WHERE name = 'Sanitation Team'
      AND department_id = departments.id
);
