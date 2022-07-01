create event AutoCleanOldData
on schedule at current_timestamp + interval 1 day
on completion preserve
do
delete low_priority from northsidecultivation.data_log where datetime < date_sub(now(), interval 30 day);