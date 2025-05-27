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
    return Client(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      street: json['street'] ?? '',
      city: json['city'] ?? '',
      country: json['country_id'] is List 
          ? json['country_id'][1] ?? ''
          : '',
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