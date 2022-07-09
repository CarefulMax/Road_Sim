road_types_list = ['Автострада', 'Шоссе', 'Тоннель']
flow_types_list = ['Детерминированный', 'Случайный']
speed_types_list = ['Детерминированный', 'Случайный']
distributions_list = ['Нормальный', 'Равномерный', 'Экспоненциальный']
sign_values_list = [30, 40, 50]

parameters_list = ['road_type', 'directions', 'lanes_left', 'lanes_right', 'traffic_light_phase_len',
                   'flow_type', 'deterministic_time', 'distribution_law', 'normal_exp', 'normal_disp',
                   'uniform_low', 'uniform_high', 'exponential_intensity', 'speed_type', 'det_speed', 'sign_placed',
                   'sign_x',
                   'sign_y', 'sign_value', 'sign_direction']
sign_parameters = ['sign_placed', 'sign_x', 'sign_y', 'sign_value', 'sign_direction']
non_sign_parameters = ['road_type', 'directions', 'lanes_left', 'lanes_right', 'traffic_light_phase_len',
                       'flow_type', 'deterministic_time', 'speed_type', 'det_speed', 'distribution_law', 'normal_exp',
                       'normal_disp', 'uniform_low', 'uniform_high', 'exponential_intensity']

road_settings = {
    'lane_width': 50,  # 24, 50
    'highest_y': 285,
    'middle_y': 300,
    'lowest y': 315}

default_settings = {
    'road_type': 'Автострада',
    'directions': 1,
    'lanes_left': 1,
    'lanes_right': 1,
    'traffic_light_phase_len': 50,
    'flow_type': 'Детерминированный',
    'deterministic_time': 20,
    'distribution_law': 'Нормальный',
    'normal_exp': 20,
    'normal_disp': 7,
    'uniform_low': 15,
    'uniform_high': 25,
    'exponential_intensity': 0.1,
    'speed_type': 'Детерминированный',
    'det_speed': 120,
    'sign_placed': False,
    'sign_x': -100,
    'sign_y': -100,
    'sign_value': 40,
    'sign_direction': 'Влево',
}

model_settings = {
    'road_type': 'Шоссе',
    'directions': 2,
    'lanes_left': 3,
    'lanes_right': 3,
    'traffic_light_phase_len': 50,
    'flow_type': 'Случайный',
    'deterministic_time': 20,
    'distribution_law': 'Экспоненциальный',
    'normal_exp': 20,
    'normal_disp': 7,
    'uniform_low': 15,
    'uniform_high': 25,
    'exponential_intensity': 0.1,
    'speed_type': 'Детерминированный',
    'det_speed': 120,
    'sign_placed': True,
    'sign_x': -300,  # -100
    'sign_y': -300,  # -100
    'sign_value': 40,
    'sign_direction': 'Влево',
}

debug_settings = {
    'headcar_mode': False,  # Если True - можно выбрать головной автомобиль на любом типе дороги
    'stop_mode': False,  # Если True - стоящие автомобили не будут двигаться
    'all_lanes_spawn_mode': False  # Если True - автомобили спавнятся на всех полосах
}


def reset_sign_parameters():
    for key in sign_parameters:
        model_settings[key] = default_settings[key]
