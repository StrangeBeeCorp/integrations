/*---
thehive:
  name: Check IP RFC 1918/4193
  mode: Enabled
  definition: Check_ip_RFC
  description: Checks the IP Observable type and tags it as "ip:public", "ip:private", or "ip:invalid" based on RFC 1918/4193. For both IPv4 and IPv6.
  type: Notifier
  vendor: Generic
  kind: function
  version: 1.0.0
---*/

// Notification trigger: ObservableCreated

function handle(input, context) {
    
    // Check if we have an object
    if (!input.object) {
        console.log("No object found in input");
        return;
    }
    
    const observable = input.object;
    
    // Check if this is an IP observable
    if (observable.dataType !== "ip") {
        console.log(`Observable type is '${observable.dataType}', not 'ip' - skipping`);
        return;
    }
    
    const ip = observable.data;
    const observableId = observable._id;
    const currentTags = observable.tags || [];
    
    console.log(`Processing IP observable: ${ip} (ID: ${observableId})`);
    console.log(`Current tags: ${JSON.stringify(currentTags)}`);
    
    // Step 1: Validate IP format (IPv4 or IPv6)
    const ipVersion = getIPVersion(ip);
    
    if (ipVersion === 0) {
        console.log(`IP ${ip} is INVALID (neither valid IPv4 nor IPv6)`);
        updateIPTag(context, observableId, currentTags, "ip:invalid");
        return;
    }
    
    console.log(`IP ${ip} is valid IPv${ipVersion}`);
    
    // Step 2: Check if IP is private or public
    const isPrivate = ipVersion === 4 ? isPrivateIPv4(ip) : isPrivateIPv6(ip);
    const newTag = isPrivate ? "ip:private" : "ip:public";
    
    console.log(`IP ${ip} is ${isPrivate ? 'private' : 'public'}`);
    updateIPTag(context, observableId, currentTags, newTag);
}

// Function to update IP tag and remove others
function updateIPTag(context, observableId, currentTags, newTag) {
    const possibleTags = ["ip:private", "ip:public", "ip:invalid"];
    
    // Check if tag already exists
    if (currentTags.includes(newTag)) {
        console.log(`Tag '${newTag}' already present, no update needed`);
        return;
    }
    
    // Build update object
    const updateObj = { addTags: [newTag] };
    
    // Remove other IP tags if present
    const tagsToRemove = possibleTags.filter(tag => tag !== newTag && currentTags.includes(tag));
    if (tagsToRemove.length > 0) {
        console.log(`Removing tags: ${JSON.stringify(tagsToRemove)}`);
        updateObj.removeTags = tagsToRemove;
    }
    
    console.log(`Adding tag '${newTag}'`);
    context.observable.update(observableId, updateObj);
    console.log("Tags updated successfully");
}

// Function to determine IP version
// Returns: 4 for IPv4, 6 for IPv6, 0 for invalid
function getIPVersion(ip) {
    if (isValidIPv4(ip)) {
        return 4;
    }
    if (isValidIPv6(ip)) {
        return 6;
    }
    return 0;
}

// Function to validate IPv4 format
function isValidIPv4(ip) {
    const parts = ip.split('.');
    
    // Must have exactly 4 octets
    if (parts.length !== 4) {
        return false;
    }
    
    // Each octet must be a valid number between 0 and 255
    for (let part of parts) {
        const num = Number(part);
        
        // Check if it's a valid number
        if (isNaN(num)) {
            return false;
        }
        
        // Check range
        if (num < 0 || num > 255) {
            return false;
        }
        
        // Check for leading zeros (e.g., "192.168.01.1" is technically invalid)
        if (part.length > 1 && part[0] === '0') {
            return false;
        }
    }
    
    return true;
}

// Function to validate IPv6 format
function isValidIPv6(ip) {
    // Handle IPv6 with IPv4 suffix (e.g., ::ffff:192.168.1.1)
    const ipv4SuffixMatch = ip.match(/^(.+):(\d+\.\d+\.\d+\.\d+)$/);
    if (ipv4SuffixMatch) {
        const ipv6Part = ipv4SuffixMatch[1];
        const ipv4Part = ipv4SuffixMatch[2];
        
        // Validate IPv4 part
        if (!isValidIPv4(ipv4Part)) {
            return false;
        }
        
        // Continue validating the IPv6 part
        ip = ipv6Part + ':0:0';
    }
    
    // Check for valid characters
    if (!/^[0-9a-fA-F:]+$/.test(ip)) {
        return false;
    }
    
    // Split by '::'
    const parts = ip.split('::');
    
    // Can have at most one '::'
    if (parts.length > 2) {
        return false;
    }
    
    // If we have '::', validate both sides
    if (parts.length === 2) {
        const left = parts[0] ? parts[0].split(':') : [];
        const right = parts[1] ? parts[1].split(':') : [];
        
        // Total groups must be <= 8
        if (left.length + right.length > 7) {
            return false;
        }
        
        // Validate each group
        const allGroups = [...left, ...right];
        for (let group of allGroups) {
            if (group.length === 0 || group.length > 4) {
                return false;
            }
            if (!/^[0-9a-fA-F]+$/.test(group)) {
                return false;
            }
        }
        
        return true;
    }
    
    // No '::' - must have exactly 8 groups
    const groups = ip.split(':');
    if (groups.length !== 8) {
        return false;
    }
    
    // Validate each group
    for (let group of groups) {
        if (group.length === 0 || group.length > 4) {
            return false;
        }
        if (!/^[0-9a-fA-F]+$/.test(group)) {
            return false;
        }
    }
    
    return true;
}

// Function to check if IPv4 is private
function isPrivateIPv4(ip) {
    const parts = ip.split('.').map(Number);
    
    // RFC 1918 private ranges
    // 10.0.0.0/8
    if (parts[0] === 10) {
        return true;
    }
    
    // 172.16.0.0/12 (172.16.0.0 to 172.31.255.255)
    if (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) {
        return true;
    }
    
    // 192.168.0.0/16
    if (parts[0] === 192 && parts[1] === 168) {
        return true;
    }
    
    // Link-local: 169.254.0.0/16
    if (parts[0] === 169 && parts[1] === 254) {
        return true;
    }
    
    // Loopback: 127.0.0.0/8
    if (parts[0] === 127) {
        return true;
    }
    
    return false;
}

// Function to check if IPv6 is private
function isPrivateIPv6(ip) {
    // Normalize IPv6 (expand :: and convert to lowercase)
    const normalized = normalizeIPv6(ip);
    
    if (!normalized) {
        return false;
    }
    
    const firstGroup = normalized.split(':')[0];
    const firstByte = parseInt(firstGroup, 16);
    
    // Unique Local Addresses (ULA): fc00::/7 (fc00:: to fdff::)
    if (firstGroup.startsWith('fc') || firstGroup.startsWith('fd')) {
        return true;
    }
    
    // Link-local: fe80::/10
    if (firstGroup === 'fe80') {
        return true;
    }
    
    // Loopback: ::1
    if (ip === '::1' || normalized === '0000:0000:0000:0000:0000:0000:0000:0001') {
        return true;
    }
    
    // IPv4-mapped IPv6: ::ffff:0:0/96 (check if the mapped IPv4 is private)
    if (normalized.startsWith('0000:0000:0000:0000:0000:ffff:')) {
        // Extract IPv4 part and check
        const ipv4Match = ip.match(/:(\d+\.\d+\.\d+\.\d+)$/);
        if (ipv4Match) {
            return isPrivateIPv4(ipv4Match[1]);
        }
    }
    
    return false;
}

// Function to normalize IPv6 address for easier comparison
function normalizeIPv6(ip) {
    try {
        // Handle IPv4-mapped addresses
        const ipv4Match = ip.match(/^(.+):(\d+\.\d+\.\d+\.\d+)$/);
        if (ipv4Match) {
            const ipv6Part = ipv4Match[1];
            const ipv4Part = ipv4Match[2];
            const ipv4Hex = ipv4Part.split('.').map(octet => 
                parseInt(octet).toString(16).padStart(2, '0')
            ).join('');
            ip = ipv6Part + ':' + ipv4Hex.slice(0, 4) + ':' + ipv4Hex.slice(4);
        }
        
        // Split by '::'
        const parts = ip.split('::');
        
        if (parts.length === 2) {
            const left = parts[0] ? parts[0].split(':') : [];
            const right = parts[1] ? parts[1].split(':') : [];
            const zeros = 8 - left.length - right.length;
            
            const middle = Array(zeros).fill('0000');
            const allGroups = [...left, ...middle, ...right];
            
            return allGroups.map(g => g.padStart(4, '0')).join(':');
        }
        
        // No '::'
        return ip.split(':').map(g => g.padStart(4, '0')).join(':');
    } catch (e) {
        return null;
    }
}