from manimlib import *
import numpy as np

PHYSICS_RESULTS_TABLE = {
    0:0,
    1:0,
    2:0,
    3:0,
    4:0,
    5:100,
    6:109,
    7:118,
    8:125,
    9:131,
    10:134,
    11:137,
    12:140,
    13:143,
    14:145,
    15:147,
    16:148,
    17:149,
    18:150,
    19:151,
    20:152,
    21:156,
    22:160,
    23:164,
    24:166,
    25:169,
    26:173,
    27:176,
    28:179,
    29:184,
    30:189,
    31:194,
    32:200
}

fluct = 0

def pmf(p, n, k):
    return math.comb(n, k)*(p**k)*((1-p)**(n-k))

def wbd(n, k):
    distribution = np.array([pmf(i/n, n, i) * pmf(i/n, n, k) for i in range(n+1)])
    return  distribution / sum(distribution)

def bd(p, n):
    return [pmf(p, n, i) for i in range(n+1)]

def bdsum(plist, n):
    bds = [np.array(bd(i/n, n))*plist[i] for i in range(n+1)]
    bds = list(zip(*bds))
    return [sum(bd)/sum(plist) for bd in bds]

def swbd(i, n, k):
    global fluct
    sbd = np.array(bd(np.float128(i/n), n))
    fluct += sbd[k]
    return sbd * sbd[k]

def wbdsum(n, k):
    global fluct
    fluct = 0
    wbds = [swbd(i, n, k) for i in range(n+1)]
    wbds = list(zip(*wbds))
    return [sum(wbd)/fluct for wbd in wbds]

def pseudodictify(List):
    return [[e,i] for i, e in enumerate(List)]

def inverse(dict):
    return {dict[i]:i for i in dict}

def condense(arr, t):
    return list(np.array(arr[:-1]).reshape(-1,t).sum(axis=1)) + [arr[-1]]

def educated_guess(k, n, t):
    return bdsum(condense(wbd(n, k), t), 32)

class Estimator(Scene):
    drag_to_pan = False

    def construct(self):
        successes = int(input())
        trials = int(input())
        blocks = trials // 32
        default_scores_text = Text("Average given score:")
        default_scores = Text(f"""{PHYSICS_RESULTS_TABLE[math.floor(successes/trials*32)]}-{PHYSICS_RESULTS_TABLE[math.ceil(successes/trials*32)]}""")
        default_scores_text.to_edge(UP + LEFT)
        default_scores.next_to(default_scores_text, RIGHT)
        self.play(Write(default_scores_text))
        self.play(Write(default_scores))


        blind_text = Text("Known probability assumption", font_size = 28)
        blind_estimate = bd(successes/trials, 32)
        blind_mean = sum([blind_estimate[i]*i for i in range(33)])
        blind_fail = sum(blind_estimate[:5])
        blind_perfect = blind_estimate[-1]
        blind_mean_text = Text(f"Mean: {PHYSICS_RESULTS_TABLE[math.floor(blind_mean)]:.2f}", font_size = 20)
        blind_fail_text = Text(f"Failure chance: {blind_fail*100:.2f}%", font_size = 20)
        blind_perfect_text = Text(f"Perfect chance: {blind_perfect*100:.2f}%", font_size = 20)
        blind_chart = BarChart(
            values=blind_estimate,
            height=3.5,
            width=5,
            max_value=0.5,
            bar_stroke_width=1,
            bar_names=[PHYSICS_RESULTS_TABLE[i] for i in range(33)],
            bar_label_scale_val=0.2
        )
        blind_chart.to_corner(LEFT + DOWN)
        top_blinds = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(blind_estimate))), reverse=True)[:3]):
            top_blinds.append(Text(f"Value N{i+1}: {PHYSICS_RESULTS_TABLE[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_blinds[-1].next_to(blind_chart, UP)
                top_blinds[-1].align_to(blind_chart, RIGHT)
            else:
                top_blinds[-1].next_to(top_blinds[-2], UP)
                top_blinds[-1].align_to(top_blinds[-2], RIGHT)
        blind_mean_text.next_to(blind_chart, UP)
        blind_mean_text.align_to(blind_chart, LEFT)
        blind_fail_text.next_to(blind_mean_text, UP)
        blind_fail_text.align_to(blind_mean_text, LEFT)
        blind_perfect_text.next_to(blind_fail_text, UP)
        blind_perfect_text.align_to(blind_fail_text, LEFT)
        blind_text.next_to(blind_perfect_text, UP)
        blind_text.align_to(blind_chart, RIGHT)
        self.play(Write(blind_text))
        self.add(blind_chart)
        self.play(Write(blind_mean_text))
        self.play(Write(blind_fail_text))
        self.play(Write(blind_perfect_text))
        for e in top_blinds:
            self.play(Write(e))

        educated_text = Text("Weighted probability guesses", font_size = 28)
        educated_estimate = educated_guess(successes, trials, blocks)
        educated_mean = sum([educated_estimate[i]*i for i in range(33)])
        educated_fail = sum(educated_estimate[:5])
        educated_perfect = educated_estimate[-1]
        educated_mean_text = Text(f"Mean: {PHYSICS_RESULTS_TABLE[math.floor(educated_mean)]:.2f}", font_size = 20)
        educated_fail_text = Text(f"Failure chance: {educated_fail*100:.2f}%", font_size = 20)
        educated_perfect_text = Text(f"Perfect chance: {educated_perfect*100:.2f}%", font_size = 20)
        educated_chart = BarChart(
            values=educated_estimate,
            height=3.5,
            width=5,
            max_value=0.5,
            bar_stroke_width=1,
            bar_names=[PHYSICS_RESULTS_TABLE[i] for i in range(33)],
            bar_label_scale_val=0.2
        )
        educated_chart.to_corner(RIGHT + DOWN)
        top_educated = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(educated_estimate))), reverse=True)[:3]):
            top_educated.append(Text(f"Value N{i+1}: {PHYSICS_RESULTS_TABLE[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_educated[-1].next_to(educated_chart, UP)
                top_educated[-1].align_to(educated_chart, RIGHT)
            else:
                top_educated[-1].next_to(top_educated[-2], UP)
                top_educated[-1].align_to(top_educated[-2], RIGHT)
        educated_mean_text.next_to(educated_chart, UP)
        educated_mean_text.align_to(educated_chart, LEFT)
        educated_fail_text.next_to(educated_mean_text, UP)
        educated_fail_text.align_to(educated_mean_text, LEFT)
        educated_perfect_text.next_to(educated_fail_text, UP)
        educated_perfect_text.align_to(educated_fail_text, LEFT)
        educated_text.next_to(educated_perfect_text, UP)
        educated_text.align_to(educated_chart, RIGHT)
        self.play(Write(educated_text))
        self.add(educated_chart)
        self.play(Write(educated_mean_text))
        self.play(Write(educated_fail_text))
        self.play(Write(educated_perfect_text))
        for e in top_educated:
            self.play(Write(e))


print(sum(wbd(200, 100)))
#sums = wbdsum(32, 27)
#print(np.subtract(sums, bd(27/32, 32)), sum(sums), sum(bd(np.float128(27/32), 32)))