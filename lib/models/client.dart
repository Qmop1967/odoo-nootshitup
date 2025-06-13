class Client {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String street;
  final String city;
  final String country;

  Client({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.street,
    required this.city,
    required this.country,
  });

  factory Client.fromJson(Map<String, dynamic> json) {
    // Helper function to safely get string value
    String safeString(dynamic value) {
      if (value == null || value == false) return '';
      return value.toString();
    }

    // Helper function to get phone number (try mobile first, then phone)
    String getPhoneNumber() {
      String mobile = safeString(json['mobile']);
      String phone = safeString(json['phone']);
      
      if (mobile.isNotEmpty) return mobile;
      if (phone.isNotEmpty) return phone;
      return '';
    }

    // Helper function to get country name from country_id
    String getCountryName() {
      var countryId = json['country_id'];
      if (countryId is List && countryId.length > 1) {
        return safeString(countryId[1]);
      }
      return safeString(countryId);
    }

    return Client(
      id: json['id'] ?? 0,
      name: safeString(json['name']),
      email: safeString(json['email']),
      phone: getPhoneNumber(),
      street: safeString(json['street']),
      city: safeString(json['city']),
      country: getCountryName(),
    );
  }

  String get fullAddress {
    List<String> addressParts = [];
    if (street.isNotEmpty) addressParts.add(street);
    if (city.isNotEmpty) addressParts.add(city);
    if (country.isNotEmpty) addressParts.add(country);
    return addressParts.join(', ');
  }
} 