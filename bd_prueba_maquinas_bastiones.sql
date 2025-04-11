CREATE TABLE IF NOT EXISTS machines (
    name VARCHAR(50) PRIMARY KEY,
    ip VARCHAR(15) NOT NULL,
    country VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS bastions (
    id SERIAL PRIMARY KEY,
    bastion_ip VARCHAR(15) NOT NULL,
    country VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL
);

INSERT INTO bastions (bastion_ip, country, environment) VALUES
('192.168.57.10', 'Chile', 'unico'),
('10.20.20.1', 'Peru', 'production'),
('10.20.20.2', 'Peru', 'non_production'),
('10.20.20.3', 'Peru', 'non_banking'),
('10.30.30.1', 'Colombia', 'site_1'),
('10.30.30.2', 'Colombia', 'site_2');

INSERT INTO machines (name, ip, country, environment) VALUES
('destination', '192.168.58.10', 'Chile', 'unico'),
('test-server-1', '192.168.20.10', 'Peru', 'production'),
('test-server-2', '192.168.21.10', 'Peru', 'non_production'),
('test-server-3', '192.168.22.10', 'Peru', 'non_banking'),
('test-server-4', '192.168.30.10', 'Colombia', 'site_1'),
('test-server-5', '192.168.31.10', 'Colombia', 'site_2');

