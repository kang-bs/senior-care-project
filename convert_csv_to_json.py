import csv
import json
from collections import OrderedDict
import os

csv_path = '국토교통부_전국 법정동_20250415.csv'
sido_path = 'data/sido.json'
sigungu_path = 'data/sigungu.json'
dong_path = 'data/dong.json'

sido_set = OrderedDict()
sigungu_set = OrderedDict()
dong_set = OrderedDict()

with open(csv_path, encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = row['법정동코드'].strip()
        is_exist = row['삭제일자'].strip()
        name = f"{row['시도명'].strip()} {row['시군구명'].strip()} {row['읍면동명'].strip()}"

        if is_exist:  # 삭제일자가 값이 있으면 폐지된 동
            continue

        sido_code = code[:2]
        sigungu_code = code[:5]
        dong_code = code[:10]

        sido_name = row['시도명'].strip()
        sigungu_name = f"{row['시도명'].strip()} {row['시군구명'].strip()}"

        if sido_code not in sido_set:
            sido_set[sido_code] = sido_name

        if sigungu_code not in sigungu_set:
            sigungu_set[sigungu_code] = {
                "code": sigungu_code,
                "name": sigungu_name,
                "sido_code": sido_code
            }

        if dong_code not in dong_set:
            dong_set[dong_code] = {
                "code": dong_code,
                "name": name,
                "sigungu_code": sigungu_code
            }

os.makedirs('data', exist_ok=True)

with open(sido_path, 'w', encoding='utf-8') as f:
    json.dump([{"code": k, "name": v} for k, v in sido_set.items()], f, ensure_ascii=False, indent=2)

with open(sigungu_path, 'w', encoding='utf-8') as f:
    json.dump(list(sigungu_set.values()), f, ensure_ascii=False, indent=2)

with open(dong_path, 'w', encoding='utf-8') as f:
    json.dump(list(dong_set.values()), f, ensure_ascii=False, indent=2)

print("✅ 변환 완료: sido.json / sigungu.json / dong.json")