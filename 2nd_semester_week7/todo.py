from __future__ import annotations

import csv
import os
from typing import Dict, List

from fastapi import APIRouter, Body, FastAPI, HTTPException

app = FastAPI()
router = APIRouter()

todo_list: List[Dict] = []

CSV_FILE = 'todo.csv'
CSV_FIELDS = ['id', 'title', 'description']


def _ensure_csv_exists() -> None:
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()


def _load_from_csv() -> None:
    _ensure_csv_exists()
    todo_list.clear()

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row_id = int(row['id']) if row.get('id') else 0
            todo_list.append(
                {
                    'id': row_id,
                    'title': row.get('title', ''),
                    'description': row.get('description', ''),
                }
            )


def _save_to_csv() -> None:
    _ensure_csv_exists()

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in todo_list:
            writer.writerow(
                {
                    'id': item.get('id', 0),
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                }
            )


def _get_next_id() -> int:
    if not todo_list:
        return 1
    return max(item.get('id', 0) for item in todo_list) + 1


@router.post('/todo/add')
def add_todo(payload: Dict = Body(...)) -> Dict:
    if not payload:
        raise HTTPException(
            status_code=400,
            detail='입력 Dict가 비어 있습니다.',
        )

    title = payload.get('title')
    if title is None or str(title).strip() == '':
        raise HTTPException(
            status_code=400,
            detail='title은 필수입니다.',
        )

    description = payload.get('description', '')
    _load_from_csv()

    new_item = {
        'id': _get_next_id(),
        'title': str(title).strip(),
        'description': str(description).strip(),
    }
    todo_list.append(new_item)
    _save_to_csv()

    return {
        'message': 'todo가 추가되었습니다.',
        'item': new_item,
    }


@router.get('/todo/list')
def retrieve_todo() -> Dict:
    _load_from_csv()
    return {
        'count': len(todo_list),
        'items': todo_list,
    }


app.include_router(router)
