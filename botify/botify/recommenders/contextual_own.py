from .random import Random
from .recommender import Recommender
import random


class ContextualOwn(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog, history):
        self.tracks_redis = tracks_redis
        self.fallback = Random(tracks_redis)
        self.catalog = catalog
        self.history = history

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        for key, value in self.history[user].items():
            if value > 0.8:
                prev_track = key
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        tracks = self.history[user].keys()
        for el in recommendations:
            if el not in tracks:
                return el
        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]

