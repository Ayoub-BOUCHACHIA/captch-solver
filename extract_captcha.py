from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PIL import Image
import cv2
import pytesseract
import numpy
from scipy.ndimage import gaussian_filter
from PIL import ImageFilter

# Initialize the WebDriver (make sure you have the correct driver installed)
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Open the page containing the blob URL
driver.get("https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4566/cgu/")

# Allow some time for the page to load completely
time.sleep(5)

# Find the element containing the blob URL
blob_element = driver.find_element(By.XPATH, '//*[@id="captchaFR_CaptchaImage"]')  # Modify this XPath to target the correct element
blob_url = blob_element.get_attribute("src")
print('url : ', blob_url)
image_path = 'blob_image.png'
blob_element.screenshot(image_path)

time.sleep(4)

def solve_captcha(filename):
    # thresold1 on the first stage
    th1 = 140
    th2 = 140  # threshold after blurring
    sig = 1.5  # the blurring sigma

    original = Image.open(filename)
    original.save("original.png")  # reading the image from the request
    black_and_white = original.convert("L")  # converting to black and white
    black_and_white.save("black_and_white.png")
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    first_threshold.save("first_threshold.png")
    blur = numpy.array(first_threshold)  # create an image array
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blurred.save("blurred.png")
    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save("final.png")
    number = pytesseract.image_to_string(Image.open('final.png'), lang='eng',
                                         config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()

    print("RESULT OF CAPTCHA:")
    print(number)
    print("===================")
    return number

solve_captcha(image_path)

# Function to preprocess the image
def preprocess_image(image_path):
    # Load the image using OpenCV
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Resize the image to enhance OCR accuracy
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    
    # Apply thresholding to get a binary image
    _, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # Remove noise
    img_bin = cv2.medianBlur(img_bin, 3)
    
    # Invert image colors for better OCR
    img_bin = cv2.bitwise_not(img_bin)
    
    return img_bin

preprocessed_image = preprocess_image(image_path)
cv2.imwrite("final.png", preprocessed_image)
pil_image = Image.fromarray(preprocessed_image)

custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
captcha_text = pytesseract.image_to_string(pil_image, config=custom_config)
# Print the extracted text
print('---> ',captcha_text)

custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
captcha_text = pytesseract.image_to_string(pil_image, config=custom_config)
# Print the extracted text
print('---> ',captcha_text)


driver.quit()
