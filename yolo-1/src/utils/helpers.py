def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

def non_max_suppression(boxes, scores, threshold):
    if len(boxes) == 0:
        return []

    indices = scores.argsort()[::-1]
    selected_indices = []

    while len(indices) > 0:
        current_index = indices[0]
        selected_indices.append(current_index)

        current_box = boxes[current_index]
        indices = indices[1:]

        indices = [i for i in indices if calculate_iou(current_box, boxes[i]) < threshold]

    return selected_indices

def draw_boxes(frame, boxes, labels, colors):
    for box, label, color in zip(boxes, labels, colors):
        cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, 2)
        cv2.putText(frame, label, (int(box[0]), int(box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)