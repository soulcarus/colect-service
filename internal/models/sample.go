package models

import "time"

type Cycle struct {
	StartTime time.Time `json:"start_time" bson:"start_time"`
	EndTime   time.Time `json:"end_time" bson:"end_time"`
	Samples   []Sample  `json:"samples" bson:"samples"`
}

type Sample struct {
	Timestamp time.Time          `json:"timestamp" bson:"timestamp"`
	Values    map[string]float64 `json:"values" bson:"values"`
}
