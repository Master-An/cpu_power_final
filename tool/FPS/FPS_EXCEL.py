import os
import re
import xlwt
import sys

# 2016/09/02
# xuant@qti.qualcomm.com
# filter key word from logcat

i=0
total_fps = 0;
def parser_fps_Letv2(input):
	find_str = re.findall(r'fps:\d{0,2}.\d{0,7}',input)
	if  len(find_str) == 0:
		return ''
	else:
		s_str = re.split(':',find_str[0])
		fps_str = s_str[1]
		return fps_str

def parser_fps_andeno_device(input):
	find_str = re.findall(r'FPS:\s{1,4}\d{0,2}\.\d{0,2}',input)
	if  len(find_str) == 0:
		return ''
	else:
		s_str = re.split('  ',find_str[0])
		fps_str = s_str[1]
		return fps_str

def parser_fps_for_thermal_auto_device(input):
	find_str = re.findall(r'FPS:\s{1,4}\d{0,2}\.\d{0,2}',input)
	print find_str
	if  len(find_str) == 0:
		return ''
	else:
		s_str = re.split(' ',find_str[0])
		fps_str = s_str[1]
		return fps_str
		
def parser_fps_skipped_frames(input):
	find_str = re.findall(r'FPS:\s{1,4}\d{0,2}\.\d{0,2}',input)
	if  len(find_str) == 0:
		return ''
	else:
		s_str = re.split('  ',find_str[0])
		fps_str = s_str[1]
		return fps_str	
		
def parser_time(input):
	find_time = re.findall(r'\d\d:\d\d:\d\d.\d\d\d',input)
	return find_time
		
print ('begin analysis')

style0 = xlwt.XFStyle()
style0.num_format_str = '0.00'

if len(sys.argv) >=1:
	f = open(sys.argv[1], 'r')
	print(sys.argv[1])
else:
	print('Python paython_file.py //file_loaction')
#f = open('C:\\Users\\xuant\\Desktop\\log.txt', 'r')
book = xlwt.Workbook(encoding='utf-8')

sheet = book.add_sheet("FPS",cell_overwrite_ok=False)
 
for line in f.readlines():
	fps_val = parser_fps_for_thermal_auto_device(line)
	if len(fps_val) >= 1:
		i=i+1
		sheet.write(i,1,float(fps_val),style0)
		my_time = parser_time(line)
		sheet.write(i,0,my_time)
f.close()
book.save("fps.xls")

print 'Done'