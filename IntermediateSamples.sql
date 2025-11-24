CREATE TABLE products
   (
	id 	int,
	product	varchar(30),
	type	varchar(30),
	version	int,
	release	date
   )


CREATE TABLE products
   (
	id 	int,
	product	varchar(30),
	type	varchar(30),
	version	int,
	release	date
   );

ALTER TABLE products
ADD CONSTRAINT u_product_version
UNIQUE (product, version);

ALTER TABLE products ADD CONSTRAINT pk_products PRIMARY KEY (id)

CREATE TABLE patches
   (
	id 	int PRIMARY KEY,
	patch	int,
	product	int FOREIGN KEY REFERENCES products(id),
	release	date
   );

CREATE TABLE patches
   (
	id 	int NOT NULL,
	product_id int,
	patch 	int NOT NULL,
	release	date,
	PRIMARY KEY (id),
	CONSTRAINT fk_product_patches FOREIGN KEY (id)
	REFERENCES products(id)
   );

-- -------------------------------------------------------- --
-- The following work with the Oracle XE sample HR database --
-- -------------------------------------------------------- --

SELECT first_name, last_name
  FROM employees 
 WHERE job_id = (SELECT job_id FROM jobs WHERE job_title = 'President');

SELECT first_name || ' ' || last_name as Full_Name
  FROM employees 
 WHERE job_id = (SELECT job_id FROM jobs WHERE job_title = 'President');

SELECT job_title, 
  (SELECT count(*) FROM employees 
   WHERE job_id = jobs.job_id) AS job_count 
FROM jobs
ORDER BY job_title;

SELECT job_title, count(*) AS job_count
  FROM employees 
INNER JOIN jobs ON jobs.job_id = employees.job_id
 WHERE employees.job_id = jobs.job_id
GROUP BY job_title
ORDER BY job_title;

SELECT job_title, count(*) AS job_count
  FROM employees 
INNER JOIN jobs ON jobs.job_id = employees.job_id
 WHERE employees.job_id = jobs.job_id 
GROUP BY job_title
HAVING count(*) = 1
ORDER BY job_title;

SELECT job_title, min_salary, max_salary, avg_salary
FROM (SELECT jobs.job_id, avg(salary) AS avg_salary
    FROM jobs
   INNER JOIN employees ON jobs.job_id = employees.job_id
  GROUP BY jobs.job_id) salary_averages
INNER JOIN jobs ON jobs.job_id = salary_averages.job_id;

SELECT job_title, min_salary, max_salary, actual_min, actual_max, avg_salary
FROM 
 (SELECT jobs.job_id, max(salary) AS actual_max
    FROM jobs
   INNER JOIN employees ON jobs.job_id = employees.job_id
  GROUP BY jobs.job_id) salary_maxes
INNER JOIN jobs ON jobs.job_id = salary_maxes.job_id
INNER JOIN (SELECT jobs.job_id, avg(salary) AS avg_salary
    FROM jobs
   INNER JOIN employees ON jobs.job_id = employees.job_id
  GROUP BY jobs.job_id) salary_averages on salary_averages.job_id = jobs.job_id
INNER JOIN (SELECT jobs.job_id, min(salary) AS actual_min
    FROM jobs
   INNER JOIN employees ON jobs.job_id = employees.job_id
  GROUP BY jobs.job_id) salary_mins on salary_mins.job_id = jobs.job_id;

SELECT job_title, min_salary, max_salary, actual_min, actual_max, avg_salary
FROM
  (SELECT jobs.job_id, max(salary) AS actual_max, min(salary) AS actual_min, avg(salary) AS avg_salary
     FROM  jobs
   INNER JOIN employees ON jobs.job_id = employees.job_id
  GROUP BY jobs.job_id) salary_ags
INNER JOIN jobs ON jobs.job_id = salary_ags.job_id


create view salary_ranges

SELECT sum(salary) FROM employees;

SELECT sum(salary) from (
SELECT sum(salary) as salary, department_name
  FROM employees
INNER JOIN departments on departments.department_id  = employees.department_id
GROUP BY department_name
);

SELECT sum(salary) AS salary, department_name
  FROM employees
LEFT JOIN departments on departments.department_id  = employees.department_id
GROUP BY department_name;

SELECT sum(salary) AS salary, department_name
  FROM employees
RIGHT JOIN departments on departments.department_id  = employees.department_id
GROUP BY department_name;

SELECT sum(salary), department_name
  FROM employees
FULL JOIN departments on departments.department_id  = employees.department_id
GROUP BY department_name;

SELECT current_date FROM dual;