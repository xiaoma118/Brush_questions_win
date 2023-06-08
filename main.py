import datetime
import time
from io import BytesIO

import requests
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

from answer import db_get_user_info, add_user_info, get_info

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}


# root.place_window_center()    #让显现出的窗口居中
# root.resizable(False,False)   #让窗口不可更改大小
# root.wm_attributes('-topmost', 1)#让窗口位置其它窗口之上


class CreateWindow:
    def __init__(self, cookie=None):
        self.name = None
        self.input_value = None
        self.text_box = None
        self.root = None
        self.user_label = None
        self.table = None
        self.photo = None
        self.user_image = None
        self.user_labelframe = None
        self.cookie = cookie,
        self.user_info = None

    def entrance(self):
        self.root = ttk.Window(
            title="一键刷题",  # 设置窗口的标题
            themename="minty",  # 设置主题
            size=(1200, 700),  # 窗口的大小
            position=(100, 100),  # 窗口所在的位置
            minsize=(0, 0),  # 窗口的最小宽高
            maxsize=(1920, 1080),  # 窗口的最大宽高
            resizable=None,  # 设置窗口是否可以更改大小
            alpha=1.0,  # 设置窗口的透明度(0.0完全透明）
        )
        # 创建 ttkbootstrap 的 Style 对象
        style = ttk.Style()
        style.configure(".", font=("宋体", 11))

        # 设置按钮字体大小
        new_font_size = 14  # 设置为你想要的字体大小
        style.configure("TLabel", font=(None, new_font_size))
        style.configure("TButton", font=(None, new_font_size))

        label_frame = ttk.Labelframe(self.root, text='login', padding=15)
        label_frame.pack(fill=X, side=TOP)

        self.user_labelframe = ttk.Labelframe(self.root, text='user', padding=15)
        self.user_labelframe.pack(fill=X, side=TOP)
        self.user_label = ttk.Label(self.user_labelframe, image=self.photo)

        # self.user_label.pack(anchor=CENTER)

        label_frame2 = ttk.Labelframe(self.root, text='作业列表', padding=15, )
        label_frame2.pack(side=TOP, fill=BOTH, expand=YES)

        self.input_value = ttk.Entry(label_frame)
        self.input_value.pack(side=LEFT, padx=5, fill=X, expand=YES)

        login_bt = ttk.Button(label_frame, bootstyle=INFO, text='登入', command=self.get_input_value)
        login_bt.pack()

        # 创建表格
        # 让容器自适应大小
        label_frame2.columnconfigure(0, weight=1)
        label_frame2.columnconfigure(1, weight=1)
        label_frame2.rowconfigure(0, weight=1)

        label_frame2.grid_propagate(False)
        style.configure("Custom.Treeview", rowheight=25, borderwidth=1, relief="solid")  # 设置行高为30像素
        self.table = ttk.Treeview(label_frame2, style='Custom.Treeview')

        # 定义表格的列名
        self.table["columns"] = ("title", "id", "end_time")

        # 设置列的宽度
        # self.table.column("#0", width=50, minwidth=50, anchor=CENTER)
        self.table.column("title", width=300, minwidth=300, anchor=CENTER)
        self.table.column("id", width=60, minwidth=60, anchor=CENTER)
        self.table.column("end_time", width=200, minwidth=200, anchor=CENTER)

        # 设置表格的列名
        # self.table.heading("#0", text="ID")
        self.table.heading("title", text="标题")
        self.table.heading("id", text="编号")
        self.table.heading("end_time", text="截止时间")

        # 设置表格的高度
        # self.table["width"] = 20

        # 删除默认表头
        self.table.column("#0", width=0, stretch=ttk.NO)
        # self.table.pack(fill=BOTH, side=LEFT)
        self.table.grid(row=0, column=0, sticky=NSEW)

        # 创建TEXT文本框
        self.text_box = ttk.Text(label_frame2)
        # self.text_box.insert('end', '11111111111111111111111111')
        self.text_box.grid(row=0, column=1, sticky=NSEW)
        # 默认用户信息
        self.user_info = db_get_user_info()
        if self.user_info:
            self.get_cookie()
            self.print_to_text('为保证提交质量，每3秒一题')
        self.root.mainloop()

    def get_cookie(self):
        self.cookie = self.user_info['cookie']
        self.get_image(self.user_info['image'])
        self.get_task_list()
        return self.cookie

    def get_input_value(self):
        input_value = self.input_value.get().replace('\n', '')
        if not input_value.strip():
            self.print_to_text('cookie不能为空')
            return False
        self.cookie = input_value.strip()
        self.get_user_info()
        self.get_image(self.user_info['image'])
        self.get_task_list()

    def get_user_info(self):
        # if self.user_info:
        headers['Cookie'] = self.cookie
        url = 'https://www.yuketang.cn/v/course_meta/user_info'
        try:
            resp = requests.get(url, headers=headers)
            headers['X-Csrftoken'] = resp.cookies.get_dict()['csrftoken']

            data = resp.json()
            if data['success']:
                data = data['data']['user_profile']
                add_user_info(data, headers)
                self.user_info = db_get_user_info()
        except:
            self.print_to_text('cookie无效或已过期')

    def get_image(self, img_url):
        url = img_url  # 替换为你要显示的图片的URL
        response = requests.get(url)
        image_data = response.content

        # 将图片数据转换为PIL Image对象
        image = Image.open(BytesIO(image_data))

        # 调整图片大小（可选）
        image = image.resize((50, 50))

        # 将PIL Image对象转换为Tkinter的PhotoImage对象
        self.photo = ImageTk.PhotoImage(image)
        self.user_label.configure(image=self.photo)
        self.user_label.pack(side=LEFT)
        self.name = ttk.Label(self.user_labelframe, text=self.user_info['name'])
        self.name.pack(side=LEFT)

    def get_task_list(self):
        """
        获取作业列表
        :return:
        """
        # 先清空表格
        headers['Cookie'] = self.cookie
        headers['X-Csrftoken'] = self.user_info['token']
        for row in self.table.get_children():
            self.table.delete(row)
        url = 'https://www.yuketang.cn/v2/api/web/logs/learn/16719893?actype=15&page=0&offset=20&sort=-1'
        resp = requests.get(url=url, headers=headers)
        # print(resp.json())
        data = resp.json()['data']
        activities = data['activities']
        for av in activities:
            print(av['title'])
            if av['type'] == 19:
                score_d = av['content']['score_d']
                leaf_type_id = av['content']['leaf_type_id']
                print(leaf_type_id)
                end_time = datetime.datetime.fromtimestamp(score_d / 1000)
                self.table.insert("", "end", text="1", values=(av['title'], leaf_type_id, end_time))
        self.table.bind("<Double-1>", self.handle_double_click)

    def handle_double_click(self, event):
        item = self.table.identify("item", event.x, event.y)  # 获取点击的行
        values = self.table.item(item, "values")  # 获取行的值
        self.print_to_text('Double clicked on row:%s' % str(values))

        # 创建弹窗
        # popup = ttk.Toplevel(self.root)
        # popup.title("弹窗")

        # 创建Text小部件用于显示实时打印
        # text = ttk.Text(self.text_box)
        # text.pack(fill=BOTH)

        headers['Classroom-Id'] = '16719893'
        headers['Xtbz'] = 'ykt'

        def submit_answers(body):
            sub_url = 'https://www.yuketang.cn/mooc-api/v1/lms/exercise/problem_apply/'
            sub_resp = requests.post(url=sub_url, headers=headers, json=body, timeout=5)
            if sub_resp.status_code == 200:
                return True
            else:
                return False

        # 获取当前章节题目
        url = 'https://www.yuketang.cn/mooc-api/v1/lms/exercise/get_exercise_list/%s/' % values[1]

        resp = requests.get(url=url, headers=headers).json()
        problems = resp['data']['problems']
        # insert_info(problems, 16719893, resp['data']['exercise_id'])

        for index, p in enumerate(problems):
            subject = p['content']['Body']
            start_index = subject.find("<p>") + len("<p>")
            end_index = subject.find("</p>")
            extracted_text = subject[start_index:end_index]
            body = get_info(p['problem_id'])
            if not p['user']['is_show_answer']:
                status_code = submit_answers(body)
                # 每秒3题
                # if index % 3 == 0:
                #     time.sleep(1)
                time.sleep(3)
                if status_code:
                    self.print_to_text('题目：' + str(index + 1) + extracted_text + '============提交成功')
                else:
                    self.print_to_text('题目：' + str(index + 1) + extracted_text + '************提交失败')

            else:
                self.print_to_text('题目：' + str(index + 1) + extracted_text + '============无需重复提交')

    def get_current_remaining(self, new_id):
        """
        获取当前章节剩余数量
        :return:
        """
        current_url = 'https://www.yuketang.cn/mooc-api/v1/lms/learn/course/pub_new_pro'
        param = {"cid": "16719893", "new_id": new_id}
        cu_resp = requests.post(url=current_url, headers=headers, json=param).json()
        print(cu_resp)

    def print_to_text(self, value):
        self.text_box.insert("end", value)  # 在Text小部件中插入打印内容
        self.text_box.insert("end", "\n")  # 在Text小部件中插入打印内容
        self.text_box.see("end")  # 滚动Text小部件以确保最新的内容可见
        self.text_box.update_idletasks()

    # # 关闭弹窗的按钮
    # close_button = ttk.Button(popup, text="关闭", command=popup.destroy)
    # close_button.pack(pady=10)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    m = CreateWindow()
    m.entrance()

# {"classroom_id":16719893,"problem_id":29075923,"answer":["C"]}
