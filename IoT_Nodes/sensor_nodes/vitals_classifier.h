


    // !!! This file is generated using emlearn !!!

    #include <stdint.h>
    

static inline int32_t vitals_rf_model_tree_0(const int16_t *features, int32_t features_length) {
          if (features[1] < 94) {
              return 1;
          } else {
              if (features[0] < 54) {
                  return 1;
              } else {
                  if (features[1] < 98) {
                      return 0;
                  } else {
                      return 0;
                  }
              }
          }
        }
        

static inline int32_t vitals_rf_model_tree_1(const int16_t *features, int32_t features_length) {
          if (features[0] < 100) {
              if (features[0] < 54) {
                  return 1;
              } else {
                  if (features[0] < 71) {
                      return 0;
                  } else {
                      return 0;
                  }
              }
          } else {
              return 1;
          }
        }
        

static inline int32_t vitals_rf_model_tree_2(const int16_t *features, int32_t features_length) {
          if (features[0] < 100) {
              if (features[1] < 94) {
                  return 1;
              } else {
                  if (features[1] < 98) {
                      return 0;
                  } else {
                      return 0;
                  }
              }
          } else {
              return 1;
          }
        }
        

static inline int32_t vitals_rf_model_tree_3(const int16_t *features, int32_t features_length) {
          if (features[0] < 54) {
              return 1;
          } else {
              if (features[0] < 100) {
                  if (features[1] < 93) {
                      return 1;
                  } else {
                      return 0;
                  }
              } else {
                  return 1;
              }
          }
        }
        

static inline int32_t vitals_rf_model_tree_4(const int16_t *features, int32_t features_length) {
          if (features[1] < 94) {
              return 1;
          } else {
              if (features[1] < 98) {
                  if (features[1] < 95) {
                      return 0;
                  } else {
                      return 0;
                  }
              } else {
                  return 0;
              }
          }
        }
        

int32_t vitals_rf_model_predict(const int16_t *features, int32_t features_length) {

        int32_t votes[2] = {0,};
        int32_t _class = -1;

        _class = vitals_rf_model_tree_0(features, features_length); votes[_class] += 1;
    _class = vitals_rf_model_tree_1(features, features_length); votes[_class] += 1;
    _class = vitals_rf_model_tree_2(features, features_length); votes[_class] += 1;
    _class = vitals_rf_model_tree_3(features, features_length); votes[_class] += 1;
    _class = vitals_rf_model_tree_4(features, features_length); votes[_class] += 1;
    
        int32_t most_voted_class = -1;
        int32_t most_voted_votes = 0;
        for (int32_t i=0; i<2; i++) {

            if (votes[i] > most_voted_votes) {
                most_voted_class = i;
                most_voted_votes = votes[i];
            }
        }
        return most_voted_class;
    }
    

int vitals_rf_model_predict_proba(const int16_t *features, int32_t features_length, float *out, int out_length) {

        int32_t _class = -1;

        for (int i=0; i<out_length; i++) {
            out[i] = 0.0f;
        }

        _class = vitals_rf_model_tree_0(features, features_length); out[_class] += 1.0f;
    _class = vitals_rf_model_tree_1(features, features_length); out[_class] += 1.0f;
    _class = vitals_rf_model_tree_2(features, features_length); out[_class] += 1.0f;
    _class = vitals_rf_model_tree_3(features, features_length); out[_class] += 1.0f;
    _class = vitals_rf_model_tree_4(features, features_length); out[_class] += 1.0f;
    
        // compute mean
        for (int i=0; i<out_length; i++) {
            out[i] = out[i] / 5;
        }
        return 0;
    }
    