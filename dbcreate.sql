BEGIN;
CREATE DATABASE IF NOT EXISTS `cpis` DEFAULT CHARSET `utf8`;
USE `cpis`;

CREATE TABLE IF NOT EXISTS `host_group` (
	`id` int(11) AUTO_INCREMENT NOT NULL,
	`host_group` varchar(50) NOT NULL comment '主机组',
	PRIMARY KEY(`id`),
	KEY(`host_group`)
)
;

insert into `host_group` values(null,'内部机房'),(null,'世纪互联'),(null,'蓝汛'),(null,'光环新网 '),(null,'兆维'),(null,'佛山睿江');

CREATE TABLE IF NOT EXISTS `host` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
	`host_name` varchar(50) NOT NULL comment '主机名',
    `host_code` varchar(20) NOT NULL comment '资产管理编号',
	`host_ip` varchar(17) NOT NULL comment '主机IP',
    `host_passwd` varchar(20) NOT NULL comment '主机密码',
    `host_group` varchar(50) NOT NULL comment '主机组',
	`version_sys` varchar(100) NOT NULL default 'centos 5' comment '系统版本',
	PRIMARY KEY(`id`),
	KEY(`host_group`),
	UNIQUE(`host_name`,`host_code`,`host_ip`),
	constraint `group_of_host` foreign key(`host_group`) references `host_group`(`host_group`) on delete cascade on update cascade
)
;

CREATE TABLE IF NOT EXISTS `auth` (
	`auth_id` tinyint(1) NOT NULL PRIMARY KEY,
	`name` varchar(20) NOT NULL
)
;

insert into auth(`auth_id`,`name`) values(1,'管理员'),(2,'操作者'),(3,'执行者'),(4,'不明群众');

CREATE TABLE IF NOT EXISTS `user` (
    `user_id` int(11) AUTO_INCREMENT NOT NULL,
    `user_email` varchar(50) NOT NULL comment '用户名',
    `user_passwd` varchar(32) NOT NULL comment '用户密码',
    `user_name` varchar(10) NOT NULL comment '用户姓名',
    `user_qq` varchar(20) NOT NULL comment '联系qq',
    `user_phone` varchar(11) NOT NULL comment '联系电话',
	`auth_id` tinyint(1) NOT NULL comment '权限id',
    PRIMARY KEY(`user_id`),
    KEY(`user_email`),
	KEY(`auth_id`),
    UNIQUE(`user_email`),
	constraint `auth_of_host` foreign key(`auth_id`) references `auth`(`auth_id`) on delete cascade on update cascade
)
;



insert into user(`user_id`,`user_email`,`user_passwd`,`user_name`,`user_qq`,`user_phone`,`auth_id`) values(null,'admin@test.com','394decafe4a9e1dbde3aa304625b81d3','管理员','123456','12345678987',1),(null,'jianbing@test.com','3ccc0804fd80e34626d3a57d83005297','李健兵','222222222','11111111111',2);

CREATE TABLE IF NOT EXISTS `blog_group` (
	`id` int(11) AUTO_INCREMENT NOT NULL,
	`blog_group` varchar(20) NOT NULL,
	PRIMARY KEY(`id`),
	KEY(`blog_group`)
)
;

#mysql 5.6 laster
CREATE TABLE IF NOT EXISTS `blog` (
    `blog_id` int(11) AUTO_INCREMENT NOT NULL,
    `blog_title` varchar(50) NOT NULL,
    `blog_content` text NOT NULL,
	`blog_group` varchar(20) NOT NULL,
    `blog_mtime` timestamp NOT NULL default current_timestamp,
	`blog_ctime` timestamp NOT NULL,
    `user_id` int(11) NOT NULL,
    PRIMARY KEY(`blog_id`),
	KEY(`blog_group`),
	constraint `class_of_blog` foreign key(`blog_group`) references `blog_group`(`blog_group`) on delete cascade on update cascade
)
;

insert into `blog_group` values(null,'随写'),(null,'linux服务'),(null,'硬件'),(null,'数据库'),(null,'python'),(null,'php'),(null,'bash'),(null,'perl');

CREATE TABLE IF NOT EXISTS `reports` (
	`id` int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
	`time` timestamp NOT NULL default current_timestamp,
	`message` varchar(200) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `errors` (
	`id` int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
	`time` timestamp NOT NULL default current_timestamp,
	`message` varchar(200) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `logs` (
	`id` int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
	`time` timestamp NOT NULL default current_timestamp,
	`message` varchar(200) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `upload_file` (
	`id` int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
	`path` varchar(200) NOT NULL,
	`old_filename` varchar(100) NOT NULL,
	`new_filename` varchar(100) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `command_logs` (
	`id` int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
	`user_id` varchar(50) NOT NULL,
	`date` timestamp NOT NULL default current_timestamp,
	`host` varchar(50) NOT NULL comment '主机名',
	`ip` varchar(17) NOT NULL comment '主机IP',
	`command` varchar(200) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `history` (
	`id` int(11) AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`host_date` timestamp NOT NULL default current_timestamp,
	`cpu_use` varchar(50) NOT NULL,
	`cpu_iowait` varchar(50) NOT NULL,
	`mem_use` varchar(50) NOT NULL,
	`swap_use` varchar(50) NOT NULL,
	`root_use` varchar(50) NOT NULL,
	`data0_use` varchar(50) NOT NULL,
	`var_use` varchar(50) NOT NULL,
	`usr_use` varchar(50) NOT NULL,
	`tmp_use` varchar(50) NOT NULL,
	`cpu_load` varchar(50) NOT NULL
)
;

CREATE TABLE IF NOT EXISTS `history_host` (
	`id` int(11) AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`host_ip` varchar(17) NOT NULL,
	`host_date` timestamp NOT NULL default current_timestamp,
	`error` varchar(200),
	`cpu_use` varchar(50) NOT NULL,
	`cpu_iowait` varchar(50) NOT NULL,
	`mem_use` varchar(50) NOT NULL,
	`swap_use` varchar(50) NOT NULL,
	`root_use` varchar(50) NOT NULL,
	`data0_use` varchar(50) NOT NULL,
	`var_use` varchar(50) NOT NULL,
	`usr_use` varchar(50) NOT NULL,
	`tmp_use` varchar(50) NOT NULL,
	`cpu_load` varchar(50) NOT NULL
)
;
CREATE TABLE IF NOT EXISTS `task_status` (
	`task_status_id` tinyint(1) PRIMARY KEY NOT NULL,
	`task_status` varchar(200) NOT NULL
)
;

insert into `task_status` values(1,'等待执行'),(2,'执行成功'),(3,'执行失败');

CREATE TABLE IF NOT EXISTS `task_command` (
	`id` int(11) AUTO_INCREMENT NOT NULL,
	`task_name` varchar(50) NOT NULL,
	`task_date` timestamp NOT NULL default current_timestamp,
	`host_name` varchar(50) NOT NULL comment '主机名',
	`host_ip` varchar(17) NOT NULL comment '主机IP',
	`command` varchar(200) NOT NULL,
	`content` varchar(500),
	`task_status_id` tinyint(1) NOT NULL default 1,
	PRIMARY KEY(`id`),
	KEY(`task_status_id`),
	constraint `task_of_status` foreign key(`task_status_id`) references `task_status`(`task_status_id`) on delete cascade on update cascade
)
;


CREATE TABLE IF NOT EXISTS `task_pid` (
	`id` int(11) AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`script_name` varchar(50) NOT NULL,
	`run_time` timestamp NOT NULL default current_timestamp,
	`args` text NOT NULL,
	`pid` int(5) NOT NULL
)
;

COMMIT;
