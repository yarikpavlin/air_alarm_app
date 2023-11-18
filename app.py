# -*- coding: utf8 -*-

import os
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import requests

BASE_URL = 'https://api.ukrainealarm.com/api/v3/alerts'
ICON_GREEN = "icons/green_icon.png"
ICON_RED = "icons/red_icon.png"

headers = {'Authorization': os.environ.get('ALARM_API_KEY', ''), 'accept': 'text/json'}

# Global variables for storing region information
selected_region_id = "31"  # Default region ID
region_names = {'31': 'м. Київ', '13': 'Івано-Франківська область', '8': 'Волинська область', '18': 'Одеська область', '19': 'Полтавська область', '15': 'Кіровоградська область', '20': 'Сумська область', '9999': 'Автономна Республіка Крим', '28': 'Донецька область', '24': 'Черкаська область', '11': 'Закарпатська область', '4': 'Вінницька область', '5': 'Рівненська область', '21': 'Тернопільська область', '14': 'Київська область', '25': 'Чернігівська область', '26': 'Чернівецька область', '17': 'Миколаївська область', '23': 'Херсонська область', '16': 'Луганська область', '27': 'Львівська область', '3': 'Хмельницька область', '22': 'Харківська область', '10': 'Житомирська область', '12': 'Запорізька область', '9': 'Дніпропетровська область', '0': 'Тестовий регіон'}

# Initialize the previous_status variable
previous_status = None

def get_alerts_by_region(region_id):
    response = requests.get(url=f"{BASE_URL}/{region_id}", headers=headers)
    response.raise_for_status()
    return response.json()

def update_system_tray_icon():
    global previous_status
    global selected_region_id
    region_id = selected_region_id
    try:
        alerts = get_alerts_by_region(region_id)
        has_active_alerts = bool(alerts and alerts[0].get("activeAlerts"))

        if has_active_alerts:
            tray_icon.setIcon(QIcon(ICON_RED))
            if previous_status is None or previous_status == "safe":
                tray_icon.showMessage("Повітряна тривога", "There are active alerts!", QSystemTrayIcon.MessageIcon.Information, 5000)
        else:
            tray_icon.setIcon(QIcon(ICON_GREEN))
            if previous_status == "active":
                tray_icon.showMessage("Відбій повітрянної тривоги", "The air alarm has been lifted",
                                       QSystemTrayIcon.MessageIcon.Information, 5000)

        previous_status = "active" if has_active_alerts else "safe"

        # Update tooltip with the default region name
        tray_icon.setToolTip(f"{region_names.get(selected_region_id, 'Unknown')}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def select_region():
    global selected_region_id
    items = list(region_names.values())
    item, ok = QInputDialog.getItem(
        None, "Налаштування регіону", "Оберіть регіон:", items, 0, False, Qt.WindowType.Window
    )

    if ok and item:
        selected_region_id = next(key for key, value in region_names.items() if value == item)
        update_system_tray_icon()

def create_system_tray_icon():
    tray_icon = QSystemTrayIcon(QIcon(ICON_GREEN))
    tray_icon.setToolTip(f"{region_names.get(selected_region_id, 'Повітряна тривога')}")

    menu = QMenu()
    action_open = QAction("Налаштування", app)
    action_exit = QAction("Вихід", app)
    menu.addAction(action_open)
    menu.addAction(action_exit)

    tray_icon.setContextMenu(menu)

    action_open.triggered.connect(select_region)
    action_exit.triggered.connect(app.quit)

    timer = QTimer()
    timer.timeout.connect(update_system_tray_icon)
    timer.start(30000)  # 30 seconds

    tray_icon.show()

    return tray_icon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray_icon = create_system_tray_icon()

    sys.exit(app.exec())
