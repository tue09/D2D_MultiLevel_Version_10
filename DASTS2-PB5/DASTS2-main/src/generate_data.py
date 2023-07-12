import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def gen_on_circle(radius, center=(0, 0), n=1):
    angle = 2 * np.pi * np.random.random_sample(n)
    x = radius * np.cos(angle) + center[0]
    y = radius * np.sin(angle) + center[1]

    return x, y


def gen(num_staff, num_cus, max_wait_time, velocity):
    cus_per_staff = num_cus // num_staff + 1

    perimeter = max_wait_time * velocity
    avg_radius = perimeter / np.pi / 2
    radius_lower_bound = 0.2 * avg_radius
    radius_upper_bound = 1.2 * avg_radius

    center_angles = 2 * np.pi * np.random.random_sample(num_staff)

    result = {"x": [], "y": []}

    for center_angle in center_angles:
        radius = np.random.randint(radius_lower_bound, radius_upper_bound)
        center = (radius * np.cos(center_angle), radius * np.sin(center_angle))
        xs, ys = gen_on_circle(radius, center, cus_per_staff)
        for x, y in zip(xs, ys):
            if len(result["x"]) < num_cus:
                result["x"].append(x)
                result["y"].append(y)

    df = pd.DataFrame.from_dict(result)
    df.to_csv("data.csv")
    sns.scatterplot(data=df, x="x", y="y")
    plt.savefig("img.png")


if __name__ == '__main__':
    gen(2, 10, 2, 40)
