import matplotlib.pyplot as plt

def generate_table(data, colors, filename):
    fig, ax = plt.subplots()
    columns_num = len(data[0]) - 2
    widths = [0.15] + [0.8 / columns_num] * columns_num + [0.05]
    table = ax.table(cellText=data, cellColours=colors, loc='center', colWidths=widths)

    #modify table
    # table.scale(1, 4)
    table.auto_set_font_size(False)
    table.set_fontsize(4)
    ax.axis('off')

    #save table
    plt.savefig(f"images/{filename}.png", bbox_inches='tight', dpi=800)


def yes_no_from_int(value):
    if value == 0:
        return "No"
    elif value == 1:
        return "Yes"
    elif value == 2:
        return "Try"
    return "Unknown"