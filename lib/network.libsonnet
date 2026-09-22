{
  // Splits a CIDR block into N equal smaller subnets
  cidr_split_n(cidr, n):
    local parts = std.split(cidr, '/');
    local base_ip = parts[0];
    local mask = std.parseInt(parts[1]);

    // Recursive log2 helper function
    local log2(val) =
      if val <= 1 then 0 else 1 + log2(val / 2);

    local new_mask = mask + log2(n);

    // Parse base IP into octets
    local octets = std.map(function(x) std.parseInt(x), std.split(base_ip, '.'));
    local ip_int = (octets[0] * 16777216) + (octets[1] * 65536) + (octets[2] * 256) + octets[3];

    // Total IPs per new subnet (using the ^ operator)
    local subnet_size = std.pow(2, 32 - new_mask);

    // Generate N subnets
    std.makeArray(n, function(i)
      local sub_ip_int = ip_int + (i * subnet_size);
      local o1 = std.floor(sub_ip_int / 16777216) % 256;
      local o2 = std.floor(sub_ip_int / 65536) % 256;
      local o3 = std.floor(sub_ip_int / 256) % 256;
      local o4 = sub_ip_int % 256;

      std.format('%d.%d.%d.%d/%d', [o1, o2, o3, o4, new_mask]))
}
