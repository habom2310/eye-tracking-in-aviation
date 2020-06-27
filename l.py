import cv2
from matplotlib import pyplot as plt

img = cv2.imread("flight.jpg")

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.show()