   // lib/network.rhai

   fn parse_cidr_v4(cidr_str) {
       let slash_idx = cidr_str.index_of('/');
       if slash_idx < 0 {
           throw `Invalid CIDR format: ${cidr_str}`;
       }

       let ip_str = cidr_str.sub_string(0, slash_idx);
       let prefix = parse_int(cidr_str.sub_string(slash_idx + 1));

       let octets = ip_str.split('.');
       if octets.len() != 4 {
           throw `Invalid IPv4 format: ${ip_str}`;
       }

       let ip_num = (parse_int(octets[0]) << 24)
                  | (parse_int(octets[1]) << 16)
                  | (parse_int(octets[2]) << 8)
                  | parse_int(octets[3]);

       return #{ ip: ip_num, prefix: prefix };
   }

   fn format_ip_v4(ip_num) {
       let o1 = (ip_num >> 24) & 255;
       let o2 = (ip_num >> 16) & 255;
       let o3 = (ip_num >> 8) & 255;
       let o4 = ip_num & 255;
       return `${o1}.${o2}.${o3}.${o4}`;
   }

   // Equivalent to Rust `cidr_split_n_filter`
   fn cidr_split_n(value, args) {
       let n = args.n;
       if n == () || n <= 0 {
           throw "Argument 'n' for cidr_split_n must be a positive integer.";
       }

       let parsed = parse_cidr_v4(value);

       // Round up to next power of 2
       let num_subnets = 1;
       let additional_bits = 0;
       while num_subnets < n {
           num_subnets = num_subnets << 1;
           additional_bits += 1;
       }

       let new_prefix = parsed.prefix + additional_bits;
       if new_prefix > 32 {
           throw `Cannot split ${value} into ${n} subnets: prefix /${new_prefix} exceeds /32`;
       }

       // Mask host bits for base network address
       let host_bits = 32 - parsed.prefix;
       let base_net = (parsed.ip >> host_bits) << host_bits;

       let new_subnet_size = 1 << (32 - new_prefix);
       let subnets = [];

       for i in 0..num_subnets {
           let subnet_num = base_net + (i * new_subnet_size);
           subnets.push(`${format_ip_v4(subnet_num)}/${new_prefix}`);
       }

       return subnets;
   }
