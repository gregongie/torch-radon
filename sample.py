# from tests.astra_wrapper import AstraWrapper
from tests.utils import generate_random_images, relative_error, circle_mask
import cv2
import numpy as np
import torch
from torch_radon import Radon, RadonNoiseGenerator


def normalize(x):
    x -= np.min(x)
    x /= np.max(x)
    x *= 255
    return x.astype(np.uint8)


device = torch.device('cuda')

batch_size = 16
image_size = 128
n_angles = 256

x = cv2.resize(cv2.imread("phantom.png", 0), (image_size, image_size), interpolation=cv2.INTER_CUBIC)
#x = generate_random_images(batch_size, image_size)
angles = np.linspace(0, np.pi, n_angles).astype(np.float32)

# astra = AstraWrapper(angles)
# a_id, a_y = astra.forward(x)
# a_bp = astra.backproject(a_id, image_size, batch_size)

with torch.no_grad():
    radon = Radon(image_size).to(device)
    x = torch.FloatTensor(x).view(1, image_size, image_size) / 255
    angles = torch.FloatTensor(angles).to(device)
    x_ = x.to(device)
    y = radon.forward(x_, angles) #.cpu().numpy()
    z = radon.backprojection(y, angles)

# a_bp *= circle_mask(image_size)

# print("Forward relative error", relative_error(a_y, y.cpu().numpy()))
# print("Back relative error", relative_error(a_bp, z.cpu().numpy()))

# sinogram_delta = (a_y[0] - y[0].cpu().numpy())**2
# sinogram_delta /= np.max(sinogram_delta)/255
# cv2.imwrite("sinogram_delta.png", sinogram_delta.astype(np.uint8))

radon_noise = RadonNoiseGenerator()
print(torch.min(y), torch.max(y))

for signal in [2, 3, 4, 8, 10, 12, 14]:
    for approximate in [True, False]:
        yn = y.clone()
        radon_noise.add_noise(yn, signal, 100.0, approximate)
        z = radon.backprojection(yn, angles)[0].cpu().numpy()
        cv2.imwrite("noised.png", normalize(z))
        print(signal, approximate, torch.mean((y - yn)**2).item(), torch.min(yn), torch.max(yn))