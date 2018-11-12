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
        self.canvas = tk.Canvas(
            self, width=1000, height=1000, background='bisque')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.buttons = []

    def draw_tree(self, root_node):
        self._draw_node(root_node, 12, 12)

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


if __name__ == '__main__':
    plan_path = './samplebig.json'
    node_types.init()

    root = tk.Tk()
    tree_frame = TreeFrame(root)
    tree_frame.pack(fill="both", expand=True)

    with open(plan_path) as plan_file:
        plan_json = json.loads(plan_file.read())
        root_node = main.build_tree([plan_json[0]["Plan"]])[0]
        tree_frame.draw_tree(root_node)

    root.mainloop()
