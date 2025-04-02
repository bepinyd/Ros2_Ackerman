import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Paths to packages and files
    package_name = "ackerman_description"
    new_robot_description = get_package_share_directory(package_name)
    gazebo_ros_dir = get_package_share_directory("gazebo_ros")

    # Declare launch arguments
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(new_robot_description, "URDF", "ackerman_main.urdf.xacro"),
        description="Absolute path to robot URDF file",
    )

    world_arg = DeclareLaunchArgument(
        name="world",
        default_value=os.path.join(new_robot_description, "worlds", "empty.world"),
        description="Absolute path to Gazebo world file",
    )

    # Robot description from Xacro
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str,
    )

    # Start Gazebo Classic server
    start_gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, "launch", "gzserver.launch.py")
        )
    )

    # Start Gazebo Classic client
    start_gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, "launch", "gzclient.launch.py")
        )
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description, "use_sim_time": True},
        ],
        output="screen",
    )

   
    ackerman_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ack_cont"],  # Ensure type is passed
        output="screen",
    )
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],  # Ensure type is passed
        output="screen",
    )
    

    # Spawn robot in Gazebo Classic
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "ackermann_steering_vehicle",
            "-topic", "robot_description",
            "-x", "0", "-y", "0", "-z", "0.1"
        ],
        output="screen",
    )

  

    # Launch description
    return LaunchDescription([
        model_arg,
        world_arg,
        start_gazebo_server,
        robot_state_publisher_node,
        start_gazebo_client,
        spawn_robot,
        ackerman_controller,
        joint_state_broadcaster,
       
    ])
