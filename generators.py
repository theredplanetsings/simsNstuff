import hashlib
import numpy as np


def derive_stable_seed(base_seed, label):
    """Create a deterministic per-label seed from a user-provided base seed."""
    key = f"{int(base_seed)}:{label}".encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=4).digest()
    return int.from_bytes(digest, "little")


def _validate_non_negative_int(value, name):
    if not isinstance(value, (int, np.integer)):
        raise TypeError(f"{name} must be an integer.")
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0.")


def _validate_positive_int(value, name):
    _validate_non_negative_int(value, name)
    if value == 0:
        raise ValueError(f"{name} must be greater than 0.")


def _validate_depth_factor(depth_factor):
    if not np.isfinite(depth_factor):
        raise ValueError("depth_factor must be finite.")
    if depth_factor <= 0:
        raise ValueError("depth_factor must be greater than 0.")


def _validate_trap_efficiency(trap_efficiency):
    if not np.isfinite(trap_efficiency):
        raise ValueError("trap_efficiency must be finite.")
    if trap_efficiency < 0 or trap_efficiency > 1:
        raise ValueError("trap_efficiency must be between 0 and 1.")


def _empty_coords():
    return np.zeros((0, 3))


def generate_realistic_deposits(mineral, mode, n_deposits, seed, depth_factor, complexity):
    """Generate geologically realistic mineral deposits."""
    _validate_non_negative_int(n_deposits, "n_deposits")
    _validate_positive_int(complexity, "complexity")
    _validate_depth_factor(depth_factor)

    if n_deposits == 0:
        return _empty_coords()

    if mode not in {
        "Orebody systems",
        "Hydrothermal veins",
        "Sedimentary layers",
        "Contact metamorphic",
        "Placer deposits",
    }:
        raise ValueError(f"Unsupported mineral mode: {mode}")

    rng = np.random.default_rng(derive_stable_seed(seed, mineral))

    if mode == "Orebody systems":
        center = rng.uniform(-30, 30, size=3)
        strike = rng.uniform(0, 2 * np.pi)
        dip = rng.uniform(np.pi / 6, np.pi / 2)

        length = rng.uniform(20, 40)
        t = rng.uniform(0, length, n_deposits)

        axis = np.array([np.cos(strike), np.sin(strike), -np.sin(dip)])

        coords = []
        for pos in t:
            base_pos = center + pos * axis
            scatter = rng.normal(0, 3 + pos * 0.1, 3)
            scatter = scatter - np.dot(scatter, axis) * axis
            coords.append(base_pos + scatter)

        coords = np.array(coords)

    elif mode == "Hydrothermal veins":
        start = rng.uniform(-40, 40, size=3)
        coords = [start]

        current_pos = start.copy()
        branch_points = []

        for _ in range(n_deposits - 1):
            direction = rng.normal([0.5, 0.3, -0.2], 0.3)
            direction = direction / np.linalg.norm(direction)

            step_size = rng.uniform(1, 4)
            current_pos = current_pos + direction * step_size
            coords.append(current_pos.copy())

            if rng.random() < 0.1 and len(branch_points) < complexity:
                branch_points.append(current_pos.copy())

        for branch_start in branch_points:
            branch_length = rng.integers(5, 15)
            branch_pos = branch_start.copy()
            for _ in range(branch_length):
                if len(coords) >= n_deposits:
                    break
                direction = rng.normal([0, 0, -0.5], 0.4)
                direction = direction / np.linalg.norm(direction)
                branch_pos = branch_pos + direction * rng.uniform(1, 3)
                coords.append(branch_pos.copy())

        coords = np.array(coords[:n_deposits])

    elif mode == "Sedimentary layers":
        n_layers = rng.integers(2, complexity + 1)
        coords = []

        for layer in range(n_layers):
            layer_center = rng.uniform(-40, 40, size=3)
            layer_center[2] = -20 - layer * 10

            points_in_layer = n_deposits // n_layers
            if layer == n_layers - 1:
                points_in_layer = n_deposits - len(coords)

            for _ in range(points_in_layer):
                theta = rng.uniform(0, 2 * np.pi)
                r = rng.exponential(15)
                x = layer_center[0] + r * np.cos(theta)
                y = layer_center[1] + r * np.sin(theta)
                z = layer_center[2] + rng.normal(0, 2)
                coords.append([x, y, z])

        coords = np.array(coords)

    elif mode == "Contact metamorphic":
        intrusion_center = rng.uniform(-20, 20, size=3)
        coords = []

        for _ in range(n_deposits):
            distance = rng.exponential(8)
            theta = rng.uniform(0, 2 * np.pi)
            phi = rng.uniform(0, np.pi)

            x = intrusion_center[0] + distance * np.sin(phi) * np.cos(theta)
            y = intrusion_center[1] + distance * np.sin(phi) * np.sin(theta)
            z = intrusion_center[2] + distance * np.cos(phi)

            coords.append([x, y, z])

        coords = np.array(coords)

    else:  # Placer deposits
        valley_direction = rng.uniform(0, 2 * np.pi)
        valley_axis = np.array([np.cos(valley_direction), np.sin(valley_direction), 0])

        coords = []
        stream_center = rng.uniform(-30, 30, size=3)
        stream_center[2] = 0

        for _ in range(n_deposits):
            distance_along = rng.normal(0, 20)
            distance_across = rng.exponential(5)
            if rng.random() < 0.5:
                distance_across *= -1

            pos = stream_center + distance_along * valley_axis
            pos[0] += distance_across * valley_axis[1]
            pos[1] -= distance_across * valley_axis[0]
            pos[2] += rng.exponential(2)

            coords.append(pos)

        coords = np.array(coords)

    coords[:, 2] *= depth_factor
    return coords


def generate_petroleum_deposits(deposit_type, basin_size, reservoir_count, trap_efficiency, seed):
    """Generate realistic petroleum deposits."""
    _validate_positive_int(basin_size, "basin_size")
    _validate_non_negative_int(reservoir_count, "reservoir_count")
    _validate_trap_efficiency(trap_efficiency)

    if reservoir_count == 0 or trap_efficiency == 0:
        return _empty_coords()

    if deposit_type not in {"Oil", "Natural Gas", "Oil Shale", "Gas Hydrates"}:
        raise ValueError(f"Unsupported petroleum deposit type: {deposit_type}")

    rng = np.random.default_rng(derive_stable_seed(seed, deposit_type))

    reservoirs = []

    for _ in range(reservoir_count):
        basin_center = rng.uniform(-basin_size / 2, basin_size / 2, size=2)

        if deposit_type == "Oil":
            depth_base = rng.uniform(-3000, -1500)
            thickness = rng.uniform(50, 200)
        elif deposit_type == "Natural Gas":
            depth_base = rng.uniform(-2500, -800)
            thickness = rng.uniform(30, 150)
        elif deposit_type == "Oil Shale":
            depth_base = rng.uniform(-4000, -2000)
            thickness = rng.uniform(100, 500)
        else:  # Gas Hydrates
            depth_base = rng.uniform(-1000, -200)
            thickness = rng.uniform(20, 100)

        trap_type = rng.choice(["anticline", "fault_trap", "stratigraphic"])

        if trap_type == "anticline":
            n_points = int(100 * trap_efficiency)
            coords = []

            for _ in range(n_points):
                r = rng.exponential(basin_size / 8)
                theta = rng.uniform(0, 2 * np.pi)

                x = basin_center[0] + r * np.cos(theta)
                y = basin_center[1] + r * np.sin(theta)

                elevation_factor = np.exp(-r / (basin_size / 6))
                z = depth_base + thickness * elevation_factor + rng.normal(0, thickness / 10)

                coords.append([x, y, z])

        elif trap_type == "fault_trap":
            n_points = int(80 * trap_efficiency)
            coords = []

            fault_strike = rng.uniform(0, 2 * np.pi)
            fault_normal = np.array([-np.sin(fault_strike), np.cos(fault_strike)])

            for _ in range(n_points):
                distance_from_fault = rng.exponential(basin_size / 10)
                along_fault = rng.uniform(-basin_size / 4, basin_size / 4)

                pos = basin_center + distance_from_fault * fault_normal
                pos += along_fault * np.array([np.cos(fault_strike), np.sin(fault_strike)])

                x, y = pos
                z = depth_base + rng.uniform(0, thickness)

                coords.append([x, y, z])

        else:  # stratigraphic trap
            n_points = int(60 * trap_efficiency)
            coords = []

            for _ in range(n_points):
                x = basin_center[0] + rng.normal(0, basin_size / 6)
                y = basin_center[1] + rng.normal(0, basin_size / 6)
                z = depth_base + rng.uniform(0, thickness)

                coords.append([x, y, z])

        reservoirs.extend(coords)

    return np.array(reservoirs) if reservoirs else _empty_coords()
