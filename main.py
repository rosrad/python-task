#from run_excel import run_excels, run_excel_paralle, excel_task
from os.path import join, exists
from sql_task import sql_task

task_dir = '/home/14/ren/shared/task-excel'
database = join(task_dir,'swbd.db')
#files = ['make_fmllr','task.xlsx','decode_dnn.xlsx', 'make_fmllr.xlsx' ,'train_dnn.xlsx']
files = ['make_fmllr.xlsx','task.xlsx']
files = ['task_sql.xlsx']
excels = map(lambda x: join(task_dir, x), files)
excels = filter(lambda x: exists(x), excels)  # file must exists


tasks= {}
print 'excel files:'
for f in excels :
    print f
    tasks[f]=sql_task(excel=f,db=database)
    tasks[f].Queue()

answer = raw_input('\n continue to run these task ?\n').strip().lower()

if answer == 'yes' or answer == 'y' or answer == '':
    print 'continue the progress!'
    for t in tasks.itervalues():
        t.run().show_result()
