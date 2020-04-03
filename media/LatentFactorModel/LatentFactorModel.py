import random


class LFM:
    def __init__(self):
        self.allItemSet = set()

        self.F = 10
        self.T = 30
        self.alpha = 0.02
        self.lamb = 0.01

    def init_all_item_set(self, user_items):  # 初始化items
        self.allItemSet.clear()
        for user, items in user_items.items():
            for i, r in items.items():
                self.allItemSet.add(i)

    def init_items_pool(self, items):  # 扫描用户未行为items
        interacted_items = set(items.keys())
        items_pool = list(self.allItemSet - interacted_items)
        #    items_pool = list(allItemSet)
        return items_pool

    def rand_select_negative_sample(self, items):
        ret = dict()
        for i in items.keys():
            ret[i] = 1
        n = 0
        for i in range(0, len(items) * 3):
            items_pool = self.init_items_pool(items)
            item = items_pool[random.randint(0, len(items_pool) - 1)]
            if item in ret:
                continue
            ret[item] = 0
            n += 1
            if n > len(items):
                break
        return ret

    @staticmethod
    def predict(user, item, P, Q):
        rate = 0
        for f, puf in P[user].items():
            qif = Q[item][f]
            rate += puf * qif
        return rate

    def init_model(self, user_items):
        P = dict()
        Q = dict()
        for user, items in user_items.items():
            P[user] = dict()
            for f in range(0, self.F):
                P[user][f] = random.random()
            for i, r in items.items():
                if i not in Q:
                    Q[i] = dict()
                    for f in range(0, self.F):
                        Q[i][f] = random.random()
        return P, Q

    def latent_factor_model(self, user_items):
        self.init_all_item_set(user_items)
        [P, Q] = self.init_model(user_items)
        for step in range(0, self.T):
            for user, items in user_items.items():
                samples = self.rand_select_negative_sample(items)
                for item, rui in samples.items():
                    eui = rui - self.predict(user, item, P, Q)
                    for f in range(0, self.F):
                        P[user][f] += self.alpha * (eui * Q[item][f] - self.lamb * P[user][f])
                        Q[item][f] += self.alpha * (eui * P[user][f] - self.lamb * Q[item][f])
            self.alpha *= 0.9
        return P, Q
