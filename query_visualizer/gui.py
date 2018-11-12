import tkinter as tk
import main
import json
import node_types
import math
from tkinter import font


def button_click(event):
    print(event)


def button_hover(event, node):
    print(node)


class TreeFrame(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.button_font = font.Font(
            family='Google Sans Display', size=12, weight='bold')
        self.canvas = tk.Canvas(self, background='bisque')
        self.canvas.grid(row=0, column=0)

    def draw_tree(self, root_node):
        bbox = self._draw_node(root_node, 12, 12)
        self.canvas.configure(
            width=bbox[2] - bbox[0] + 24, height=bbox[3] - bbox[1] + 24)

    def _draw_node(self, node, x1, y1):
        child_x = x1
        left = x1
        right = -1
        top = y1
        bottom = -1
        button = tk.Button(self.canvas, text=node.node_type, padx=12,
                           bg='#6200ee', fg='white', font=self.button_font, anchor='center')
        button.bind('<Button-1>', button_click)
        button.bind('<Enter>', lambda event: button_hover(event, node))
        window = self.canvas.create_window(
            (x1, y1), window=button, anchor='nw')
        bbox = self.canvas.bbox(window)
        child_bboxes = []
        if len(node.children) == 0:
            return bbox
        for child in node.children:
            child_bbox = self._draw_node(
                child, child_x, y1 + 60)  # (x1, y1, x2, y2)
            child_x = child_bbox[2] + 20
            right = max(right, child_bbox[2])
            bottom = max(bottom, child_bbox[3])
            child_bboxes.append(child_bbox)
        x_mid = (left + right) // 2
        bbox_mid_x = (bbox[0] + bbox[2]) // 2
        self.canvas.move(window, x_mid - bbox_mid_x, 0)
        for child_bbox in child_bboxes:
            child_mid_x = (child_bbox[0] + child_bbox[2]) // 2
            self.canvas.create_line(
                x_mid, bbox[3], child_mid_x, child_bbox[1], width=2, arrow=tk.LAST)
        return left, top, right, bottom


class QueryFrame(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.text_font = font.Font(family='Fira Code Retina', size=12)
        self.text = tk.Text(self, height=10, font=self.text_font)
        self.text.grid(row=0, column=0)

    def set_query(self, query):
        self.text.delete('1.0', 'end')
        self.text.insert('end', query)


def visualize_query(root, query, plan):
    top_level = tk.Toplevel(root)
    tree_frame = TreeFrame(top_level)
    query_frame1 = QueryFrame(top_level)
    query_frame1.set_query(query)
    query_frame2 = QueryFrame(top_level)
    query_frame1.grid(row=0, column=0)
    query_frame2.grid(row=1, column=0)
    tree_frame.grid(row=0, column=1, rowspan=2)

    plan_json = json.loads(plan)
    root_node = main.build_tree([plan_json[0]['Plan']])[0]
    tree_frame.draw_tree(root_node)


if __name__ == '__main__':
    node_types.init()

    root = tk.Tk()

    button_font = font.Font(
        family='Google Sans Display', size=12, weight='bold')
    text_font = font.Font(family='Fira Code Retina', size=12)
    label_font = font.Font(family='Google Sans Display', size=12)

    query_label = tk.Label(
        root, text='Enter your SQL query here', font=label_font)
    query_text = tk.Text(root, font=text_font, height=10)
    plan_label = tk.Label(
        root, text='Enter your execution plan here', font=label_font)
    plan_text = tk.Text(root, font=text_font, height=10)

    visualize_button = tk.Button(root, text='VISUALIZE', padx=12,
                                 bg='#6200ee', fg='white', font=button_font, anchor='center')
    visualize_button.bind('<Button-1>',
                          lambda event: visualize_query(root, query_text.get('1.0', 'end-1c'), plan_text.get('1.0', 'end-1c')))

    query_label.grid(row=0, sticky='w', padx=12, pady=(12, 0))
    query_text.grid(row=1, padx=12)
    plan_label.grid(row=2, sticky='w', padx=12, pady=(12, 0))
    plan_text.grid(row=3, padx=12)
    visualize_button.grid(row=4, sticky='e', padx=12, pady=12)

    root.mainloop()
