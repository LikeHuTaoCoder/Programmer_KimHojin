from ultralytics import YOLO
import numpy as np
import cv2
from pathlib import Path
import base64
import json
class YOLOModel:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def predict(self, image_array: np.ndarray):
        res = self.model.predict(image_array, save=True, iou=0.2, conf=0.5)
        return res

    def process_results(self, res,img):
        results = []
        for r in res:
            img_copy = np.copy(r.orig_img)
            img_name = Path(r.path).stem

            cnt = 0
    
            result=dict()
            result['yolo_images']=list()
            for ci, c in enumerate(r):
                #이상해짐 다시고쳐야한다
                label = c.names[c.boxes.cls.tolist().pop()]
                b_mask = np.zeros(img_copy.shape[:2], np.uint8)

                # ✅ 윤곽선을 위한 마스크 생성
                contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
                _ = cv2.drawContours(b_mask, [contour], -1, (255, 255, 255), cv2.FILLED)


                # ✅ 윤곽선 강조
                contours, _ = cv2.findContours(b_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contour_mask = np.zeros_like(b_mask)  # 윤곽선 마스크
                _=cv2.drawContours(contour_mask, contours, -1, (255, 255, 255), 3)  # 두께 3px
                
                # ✅ 원본 이미지에 윤곽선 그리기 (흰색, 두께 3px)
                contours, _ = cv2.findContours(b_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(img_copy, contours, -1, (255, 255, 255), 3)

                # ✅ 객체 분리 (투명 배경 포함)
                isolated = np.dstack([img_copy, b_mask])

                # ✅ 객체 영역 잘라내기
                x1, y1, x2, y2 = c.boxes.xyxy.cpu().numpy().squeeze().astype(np.int32)
                iso_crop = isolated[y1:y2, x1:x2]

                # ✅ 윤곽선을 추가한 마스크 적용
                contour_crop = contour_mask[y1:y2, x1:x2]  # 잘라낸 윤곽선 부분만 사용
                iso_crop_with_contour = iso_crop.copy()

                # ✅ 윤곽선을 원본 위에 추가 (빨간색, 두께 3px)
                iso_crop_with_contour[:, :, 0][contour_crop > 0] = 255  # B 채널
                iso_crop_with_contour[:, :, 1][contour_crop > 0] = 255  # G 채널
                iso_crop_with_contour[:, :, 2][contour_crop > 0] = 255  # R 채널 (빨강)

                # locs.append(int((x1+x2)/2))
                # locs.append(int((y1+y2)/2))
                
                _, buffer = cv2.imencode(".png", iso_crop_with_contour)  # PNG로 메모리 버퍼에 저장
                base64_image = base64.b64encode(buffer).decode("utf-8")  # Base64로 인코딩
                #print(base64_image)
                #y1기준으로 나눠 맨위가 0
                obj=dict()
                obj['image']=base64_image
                obj['label']=label
                obj['loc']=[int((x1+x2))/2,int((y1+y2))/2]
                obj['scale']=[int(x2-x1),int(y2-y1)]

                result['yolo_images'].append(obj)
                # images.append(base64_image)
                #     scales.append(int(x2-x1))
                #     scales.append(int(y2-y1))
                #     labels.append(label)
                cnt += 1
                
                print(x1, y1, x2, y2)
            
            _, buffer = cv2.imencode(".png", img_copy)
            base64_image = base64.b64encode(buffer).decode("utf-8")

            result["image_with_contour"]=base64_image
            result['image_num']=cnt
            result['yolo_images'].sort(key=lambda obj: obj['loc'][0])
            results.append(result) 
        return results
