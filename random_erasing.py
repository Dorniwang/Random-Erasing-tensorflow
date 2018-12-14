import tensorflow as tf

def random_erasing(img, probability = 0.5, sl = 0.02, sh = 0.4, r1 = 0.3):
    '''
    img is a 3-D tensor and  HWC order
    '''
    height = tf.shape(img)[0]
    width = tf.shape(img)[1]
    channel = tf.shape(img)[2]
    area = tf.cast(width*height, tf.float32)

    target_area = tf.random.uniform([100], sl, sh) * area
    aspect_ratio = tf.random.uniform([100], r1, 1/r1)

    h = tf.cast(tf.round(tf.sqrt(target_area * aspect_ratio)), tf.int32)
    w = tf.cast(tf.round(tf.sqrt(target_area / aspect_ratio)), tf.int32)
    x1 = tf.clip_by_value(tf.random.uniform([100], 0, height, tf.int32) - h, 0, height)
    y1 = tf.clip_by_value(tf.random.uniform([100], 0, width, tf.int32) - w, 0, width)

    w_cond = tf.less(w, width)
    h_cond = tf.less(h, height)
    cond = tf.logical_and(w_cond, h_cond)
    cond_true_idx = tf.where(cond)
    first_true_idx = tf.reduce_min(cond_true_idx)

    erase_area = tf.cast(tf.random.uniform([h[first_true_idx], w[first_true_idx], channel], 0, 255, tf.int32), tf.uint8)

    update_row = tf.concat([img[x1[first_true_idx]:x1[first_true_idx]+h[first_true_idx], 0:y1[first_true_idx], :],
                            erase_area,
                            img[x1[first_true_idx]:x1[first_true_idx]+h[first_true_idx], y1[first_true_idx]+w[first_true_idx]:width, :]], axis=1)
    erasing_img = tf.concat([img[0:x1[first_true_idx], :, :],
                            update_row,
                            img[x1[first_true_idx]+h[first_true_idx]:height, :, :]], axis=0)

    can_find_idx = tf.cond(tf.equal(tf.reduce_sum(tf.cast(cond, tf.int32)), 0), lambda: img, lambda: erasing_img)  # if cant find True, return original img

    return tf.cond(tf.random.uniform([], 0, 1) > probability, lambda: img, lambda: can_find_idx)
