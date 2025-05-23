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
} #TO DO: move to an external file

fluct = 0

def EValue(plist: list, vlist: list):
    return sum([plist[i]*vlist[i] for i in range(len(plist))])

def standard_deviation(plist: list, vlist: list, mean, f = lambda x, mean: (x - mean)**2):
    return math.sqrt(sum([plist[i]*f(vlist[i], mean) for i in range(len(plist))]))

def bf(p, n, k):
    return math.comb(n, k)*(p**k)*((1-p)**(n-k))

def wbd(n, k):
    distribution = np.array([bf(i/n, n, k) for i in range(n+1)])
    return  distribution / sum(distribution)

def bd(p, n):
    return [bf(p, n, i) for i in range(n+1)]

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
#Way too many useless/ugly functions above, need to refactor later

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

        probabilities_distribution = condense(wbd(trials, successes), blocks)

        probability_text = Text("Knowledge estimates", font_size = 28)
        probability_mean = sum([probabilities_distribution[i]*i for i in range(33)])
        probability_variance = standard_deviation(probabilities_distribution, [i for i in range(len(PHYSICS_RESULTS_TABLE))], probability_mean)
        probability_perfect = probabilities_distribution[-1]
        probability_mean_text = Text(f"Mean: {PHYSICS_RESULTS_TABLE[math.floor(probability_mean)]:.2f}", font_size = 20)
        probability_variance_text = Text(f"Standard deviation: {probability_variance:.2f}", font_size = 20)
        probability_perfect_text = Text(f"Perfect chance: {probability_perfect*100:.2f}%", font_size = 20)
        probability_chart = BarChart(
            values=probabilities_distribution,
            height=3.5,
            width=5,
            max_value=1,
            bar_stroke_width=1,
            bar_names=[PHYSICS_RESULTS_TABLE[i] for i in range(33)],
            bar_label_scale_val=0.2
        )
        probability_chart.to_corner(LEFT + DOWN)
        top_probabilities = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(probabilities_distribution))), reverse=True)[:3]):
            top_probabilities.append(Text(f"Value N{i+1}: {PHYSICS_RESULTS_TABLE[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_probabilities[-1].next_to(probability_chart, UP)
                top_probabilities[-1].align_to(probability_chart, RIGHT)
            else:
                top_probabilities[-1].next_to(top_probabilities[-2], UP)
                top_probabilities[-1].align_to(top_probabilities[-2], RIGHT)
        probability_mean_text.next_to(probability_chart, UP)
        probability_mean_text.align_to(probability_chart, LEFT)
        probability_variance_text.next_to(probability_mean_text, UP)
        probability_variance_text.align_to(probability_mean_text, LEFT)
        probability_perfect_text.next_to(probability_variance_text, UP)
        probability_perfect_text.align_to(probability_variance_text, LEFT)
        probability_text.next_to(probability_perfect_text, UP)
        probability_text.align_to(probability_chart, RIGHT)
        self.play(Write(probability_text))
        self.add(probability_chart)
        self.play(Write(probability_mean_text))
        self.play(Write(probability_variance_text))
        self.play(Write(probability_perfect_text))
        for e in top_probabilities:
            self.play(Write(e))

        final_text = Text("Real result estimates", font_size = 28)
        final_estimate = bdsum(probabilities_distribution, 32)
        final_mean = sum([final_estimate[i]*i for i in range(33)])
        final_variance = standard_deviation(final_estimate, [i for i in range(len(PHYSICS_RESULTS_TABLE))], final_mean)
        final_perfect = final_estimate[-1]
        final_mean_text = Text(f"Mean: {PHYSICS_RESULTS_TABLE[math.floor(final_mean)]:.2f}", font_size = 20)
        final_variance_text = Text(f"Standard deviation: {final_variance:.2f}", font_size = 20)
        final_perfect_text = Text(f"Perfect chance: {final_perfect*100:.2f}%", font_size = 20)
        final_chart = BarChart(
            values=final_estimate,
            height=3.5,
            width=5,
            max_value=1,
            bar_stroke_width=1,
            bar_names=[PHYSICS_RESULTS_TABLE[i] for i in range(33)],
            bar_label_scale_val=0.2
        )
        final_chart.to_corner(RIGHT + DOWN)
        top_finals = []
        for i, e in enumerate(sorted(list(zip(pseudodictify(final_estimate))), reverse=True)[:3]):
            top_finals.append(Text(f"Value N{i+1}: {PHYSICS_RESULTS_TABLE[e[0][1]]}, {e[0][0]*100:.2f}%", font_size = 20))
            if not i:
                top_finals[-1].next_to(final_chart, UP)
                top_finals[-1].align_to(final_chart, RIGHT)
            else:
                top_finals[-1].next_to(top_finals[-2], UP)
                top_finals[-1].align_to(top_finals[-2], RIGHT)
        final_mean_text.next_to(final_chart, UP)
        final_mean_text.align_to(final_chart, LEFT)
        final_variance_text.next_to(final_mean_text, UP)
        final_variance_text.align_to(final_mean_text, LEFT)
        final_perfect_text.next_to(final_variance_text, UP)
        final_perfect_text.align_to(final_variance_text, LEFT)
        final_text.next_to(final_perfect_text, UP)
        final_text.align_to(final_chart, RIGHT)
        self.play(Write(final_text))
        self.add(final_chart)
        self.play(Write(final_mean_text))
        self.play(Write(final_variance_text))
        self.play(Write(final_perfect_text))
        for e in top_finals:
            self.play(Write(e))

