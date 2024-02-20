// Copyright 2024 Antonio Bono
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef HRI_MOVES__LED_ACTION_CLIENT_HPP_
#define HRI_MOVES__LED_ACTION_CLIENT_HPP_

#include <functional>
#include <future>
#include <memory>
#include <string>
#include <sstream>

#include "ament_index_cpp/get_package_share_directory.hpp"
#include "boost/filesystem.hpp"

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "rclcpp_components/register_node_macro.hpp"

#include "nao_lola_command_msgs/msg/head_leds.hpp"
#include "nao_lola_command_msgs/msg/right_eye_leds.hpp"
#include "nao_lola_command_msgs/msg/left_eye_leds.hpp"
#include "nao_lola_command_msgs/msg/right_ear_leds.hpp"
#include "nao_lola_command_msgs/msg/left_ear_leds.hpp"
#include "nao_lola_command_msgs/msg/chest_led.hpp"
#include "nao_lola_command_msgs/msg/right_foot_led.hpp"
#include "nao_lola_command_msgs/msg/left_foot_led.hpp"

#include "hri_interfaces/action/leds_play.hpp"
#include "hri_interfaces/msg/led_indexes.hpp"
#include "hri_interfaces/msg/led_modes.hpp"
#include "hri_interfaces/action/leds_play.hpp"

#include "std_msgs/msg/color_rgba.hpp"

namespace hri_led_action_client {

class LedsPlayActionClient : public rclcpp::Node {
 public:
	explicit LedsPlayActionClient(const rclcpp::NodeOptions & options = rclcpp::NodeOptions{});
	virtual ~LedsPlayActionClient();

	void sendGoal();
	void eyesOn();
	void headOn();

 private:

	void goalResponseCallback(
	  const rclcpp_action::ClientGoalHandle<hri_interfaces::action::LedsPlay>::SharedPtr & goal_handle);
	void feedbackCallback(
	  rclcpp_action::ClientGoalHandle<hri_interfaces::action::LedsPlay>::SharedPtr,
	  const std::shared_ptr<const hri_interfaces::action::LedsPlay::Feedback> feedback);
	void resultCallback(
	  const rclcpp_action::ClientGoalHandle<hri_interfaces::action::LedsPlay>::WrappedResult & result);


	rclcpp_action::Client<hri_interfaces::action::LedsPlay>::SharedPtr client_ptr_;


}; // LedsPlayActionClient

} // hri_led_action_client

#endif // HRI_MOVES__LED_ACTION_CLIENT_HPP_