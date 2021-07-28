create schema shepherd;
use shepherd;
create table Pool
(
	id int not null,
	constraint Pool_pk
		primary key (id)
)
comment 'Stores Pool-Level Attributes';

create table Node
(
	id int not null,
	pool_id int not null,
	name varchar(100) default 'Node' null,
	constraint Node_pk
		primary key (pool_id, id),
	constraint Node_Pool__fk
		foreign key (pool_id) references Pool (id)
			on update cascade on delete cascade
)
comment 'Stores Node-Level Attributes and Association to Pool';

create table `Update`
(
	id bigint unsigned auto_increment not null,
	pool_id int not null,
	node_id int not null,
	timestamp datetime not null,
	cpu_logical_cores int null,
	cpu_current_frequency float null,
	cpu_max_frequency float null,
	cpu_percent_usage float null,
	cpu_load_1 float null,
	cpu_load_5 float null,
	cpu_load_15 float null,
	ram_total_virtual bigint null,
	ram_used_virtual bigint null,
	ram_available_virtual bigint null,
	ram_free_virtual bigint null,
	ram_total_swap bigint null,
	ram_used_swap bigint null,
	ram_free_swap bigint null,
	ram_percent_swap float null,
	disk_read_count bigint null,
	disk_write_count bigint null,
	disk_read_bytes bigint null,
	disk_write_bytes bigint null,
	disk_read_time bigint null,
	disk_write_time bigint null,
	battery_available_percent float null,
	battery_est_remain bigint null,
	battery_plugged_in bool null,
	session_boot_time datetime null,
	session_uptime bigint null,
	constraint Update_pk
		primary key (id),
	constraint Update_Node__fk
		foreign key (pool_id, node_id) references Node (pool_id, id)
			on update cascade on delete cascade
)
comment 'Node Updates at High Frequency';

create table GPU_Update
(
	id bigint unsigned auto_increment not null,
	update_id bigint unsigned not null,
	uuid varchar(50) null,
	`load` float null,
	memory_percentage float null,
	memory_total bigint null,
	memory_used bigint null,
	driver_version varchar(50) null,
	product_identifier varchar(50) null,
	serial varchar(50) null,
	display_mode varchar(20) null,
	constraint GPU_Update_pk
		primary key (id),
	constraint GPU_Update_Update__fk
		foreign key (update_id) references `Update` (id)
			on update cascade on delete cascade
)
comment 'GPU Component of an Update';

create table Disk_Update
(
	id bigint unsigned auto_increment not null,
	update_id bigint unsigned not null,
	partition_id varchar(50) null,
	mount_point varchar(50) null,
	fstype varchar(20) null,
	total_storage bigint null,
	used_storage bigint null,
	free_storage bigint null,
	percentage_used float null,
	constraint Disk_Update_pk
		primary key (id),
	constraint Disk_Update_Update__fk
		foreign key (update_id) references `Update` (id)
			on update cascade on delete cascade
)
comment 'Disk Component of an Update';

create table Session_Update
(
	id bigint unsigned auto_increment not null,
	update_id bigint unsigned not null,
	user varchar(50) null,
	terminal varchar(50) null,
	host varchar(100) null,
	started_time datetime null,
	process_id int null,
	constraint Session_Update_pk
		primary key (id),
	constraint Session_Update_Update__fk
		foreign key (update_id) references `Update` (id)
			on update cascade on delete cascade
)
comment 'Session Component of an Update';

create table Historical_Data
(
    id int auto_increment not null,
    node_id int not null,
    pool_id int not null,
    time datetime not null,
    avg_cpu_curr_freq float null,
    avg_cpu_percent_usage float null,
    avg_cpu_load_1 float null,
    avg_cpu_load_5 float null,
    avg_cpu_load_15 float null,
    avg_ram_used_virt bigint null,
    avg_ram_used_swap bigint null,
    total_disk_avail bigint null,
    total_disk_used bigint null,
    avg_battery_avail float null,
    avg_gpu_load float null,
    avg_gpu_memory_used bigint null,
    constraint Historical_Data_pk primary key (id),
    constraint Historical_Data_Node__fk
        foreign key (pool_id, node_id) references `Node` (pool_id, id)
            on update cascade on delete cascade
);

create table Anomaly_Record(
    id int auto_increment not null,
    node_id int not null,
    pool_id int not null,
    type ENUM('cpu', 'ram', 'disk', 'gpu', 'session', 'battery', 'other') not null,
    time datetime not null,
    resolved boolean not null,
    message varchar(250) null,
    severity ENUM('low', 'medium', 'high', 'none') not null,
    constraint Anomaly_record_pk primary key (id),
    constraint Anomaly_Record_Node__fk
        foreign key (pool_id, node_id) references `Node` (pool_id, id)
            on update cascade on delete cascade
);
