import 'package:flutter/material.dart';
import '../services/odoo_service.dart';
import '../services/tsh_salesperson_service.dart';
import '../models/client.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/side_menu.dart';

class ClientsPage extends StatefulWidget {
  const ClientsPage({super.key});

  @override
  State<ClientsPage> createState() => _ClientsPageState();
}

class _ClientsPageState extends State<ClientsPage> {
  List<Client> _clients = [];
  bool _isLoading = true;
  String _searchQuery = '';
  final _odooService = OdooService();
  final _tshService = TSHSalespersonService();

  @override
  void initState() {
    super.initState();
    _loadClients();
  }

  Future<void> _loadClients() async {
    setState(() => _isLoading = true);

    try {
      print('🔄 Loading clients...');
      
      // Try TSH Salesperson service first for assigned customers
      List<Map<String, dynamic>> clientsData = [];
      
      try {
        print('📞 Trying TSH Salesperson getAssignedCustomers() method...');
        clientsData = await _tshService.getAssignedCustomers();
        print('✅ TSH Service returned ${clientsData.length} assigned customers');
        
        if (clientsData.isNotEmpty) {
          print('📊 Sample TSH customer data:');
          for (var i = 0; i < clientsData.length && i < 3; i++) {
            print('   ${i + 1}. ${clientsData[i]['name']} - ${clientsData[i]['phone'] ?? 'No phone'} - ID: ${clientsData[i]['id']}');
            print('      Raw JSON: ${clientsData[i]}');
          }
        }
      } catch (e) {
        print('❌ TSH Service failed: $e');
        
        try {
          print('📞 Trying getClients() method...');
          clientsData = await _odooService.getClients();
          print('✅ getClients() returned ${clientsData.length} items');
          
          if (clientsData.isNotEmpty) {
            print('📊 Sample getClients data:');
            for (var i = 0; i < clientsData.length && i < 3; i++) {
              print('   ${i + 1}. ${clientsData[i]['name']} - ${clientsData[i]['phone'] ?? 'No phone'} - ID: ${clientsData[i]['id']}');
              print('      Raw JSON: ${clientsData[i]}');
            }
          }
        } catch (e) {
          print('❌ getClients() failed: $e');
          
          try {
            print('📞 Trying getCustomers() method...');
            clientsData = await _odooService.getCustomers();
            print('✅ getCustomers() returned ${clientsData.length} items');
            
            if (clientsData.isNotEmpty) {
              print('📊 Sample getCustomers data:');
              for (var i = 0; i < clientsData.length && i < 3; i++) {
                print('   ${i + 1}. ${clientsData[i]['name']} - ${clientsData[i]['phone'] ?? 'No phone'} - ID: ${clientsData[i]['id']}');
                print('      Raw JSON: ${clientsData[i]}');
              }
            }
          } catch (e2) {
            print('❌ getCustomers() also failed: $e2');
            throw e2;
          }
        }
      }
      
      print('📊 Converting ${clientsData.length} raw records to Client objects...');
      
      List<Client> convertedClients = [];
      for (var i = 0; i < clientsData.length; i++) {
        try {
          var clientData = clientsData[i];
          print('🔄 Converting client ${i + 1}: ${clientData['name']}');
          print('   📋 Full raw data: $clientData');
          
          var client = Client.fromJson(clientData);
          convertedClients.add(client);
          
          if (i < 3) {
            print('   ✅ Converted: ${client.name} (${client.phone})');
          }
        } catch (e) {
          print('❌ Failed to convert client ${i + 1}: $e');
          print('   Raw data: ${clientsData[i]}');
          print('   Error details: $e');
        }
      }
      
      setState(() {
        _clients = convertedClients;
        _isLoading = false;
      });
      
      print('✅ Successfully loaded ${_clients.length} clients into UI');
      print('🎯 Filtered clients count: ${_filteredClients.length}');
      
      // Force a rebuild to ensure UI updates
      if (mounted) {
        setState(() {});
      }
      
    } catch (e) {
      print('❌ Error loading clients: $e');
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(
          content: Text('Error loading clients: $e'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 5),
        ));
      }
    }
  }

  List<Client> get _filteredClients {
    if (_searchQuery.isEmpty) return _clients;
    return _clients
        .where(
          (client) =>
              client.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
              client.email.toLowerCase().contains(_searchQuery.toLowerCase()) ||
              client.phone.toLowerCase().contains(_searchQuery.toLowerCase()),
        )
        .toList();
  }

  void _showAddClientDialog() {
    final nameController = TextEditingController();
    final emailController = TextEditingController();
    final phoneController = TextEditingController();
    final streetController = TextEditingController();
    final cityController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New Customer'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Company Name *',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Phone',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: streetController,
                decoration: const InputDecoration(
                  labelText: 'Street Address',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: cityController,
                decoration: const InputDecoration(
                  labelText: 'City',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.isNotEmpty) {
                final success = await _odooService.createCustomer(
                  name: nameController.text,
                  email: emailController.text.isEmpty
                      ? null
                      : emailController.text,
                  phone: phoneController.text.isEmpty
                      ? null
                      : phoneController.text,
                  street: streetController.text.isEmpty
                      ? null
                      : streetController.text,
                  city: cityController.text.isEmpty
                      ? null
                      : cityController.text,
                );

                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        success
                            ? 'Customer created successfully'
                            : 'Failed to create customer',
                      ),
                      backgroundColor: success ? Colors.green : Colors.red,
                    ),
                  );

                  if (success) {
                    _loadClients(); // Refresh the list
                  }
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showClientDetails(Client client) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(client.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (client.email.isNotEmpty) ...[
              const Text(
                'Email:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(client.email),
              const SizedBox(height: 8),
            ],
            if (client.phone.isNotEmpty) ...[
              const Text(
                'Phone:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(client.phone),
              const SizedBox(height: 8),
            ],
            if (client.fullAddress.isNotEmpty) ...[
              const Text(
                'Address:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(client.fullAddress),
              const SizedBox(height: 8),
            ],
            const Text(
              'Customer ID:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(client.id.toString()),
          ],
        ),
        actions: [
          if (_odooService.isAdmin)
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                // TODO: Edit customer functionality
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Edit customer feature coming soon'),
                  ),
                );
              },
              child: const Text('Edit'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Customers'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadClients),
        ],
      ),
      drawer: const SideMenu(),
      body: Column(
        children: [
          // Search Bar
          Container(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search customers...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
          ),

          // Summary Card
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E88E5), Color(0xFF1565C0)],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.people, color: Colors.white, size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Total Customers',
                        style: TextStyle(color: Colors.white70),
                      ),
                      Text(
                        '${_clients.length}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                if (_searchQuery.isNotEmpty)
                  Text(
                    '${_filteredClients.length} found',
                    style: const TextStyle(color: Colors.white70),
                  ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Clients List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadClients,
                    child: _filteredClients.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  _searchQuery.isEmpty
                                      ? Icons.people_outline
                                      : Icons.search_off,
                                  size: 64,
                                  color: Colors.grey,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  _searchQuery.isEmpty
                                      ? 'No customers found'
                                      : 'No customers match your search',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    color: Colors.grey,
                                  ),
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  'Debug: ${_clients.length} total clients loaded',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Colors.orange,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                ElevatedButton(
                                  onPressed: () {
                                    print('🔍 Debug button pressed');
                                    print('📊 _clients.length: ${_clients.length}');
                                    print('📊 _filteredClients.length: ${_filteredClients.length}');
                                    print('📊 _searchQuery: "$_searchQuery"');
                                    print('📊 _isLoading: $_isLoading');
                                    
                                    if (_clients.isNotEmpty) {
                                      print('📋 First 3 clients:');
                                      for (var i = 0; i < _clients.length && i < 3; i++) {
                                        print('   ${i + 1}. ${_clients[i].name} (ID: ${_clients[i].id})');
                                      }
                                    }
                                    
                                    // Force refresh
                                    _loadClients();
                                  },
                                  child: const Text('Debug & Refresh'),
                                ),
                                if (_searchQuery.isEmpty &&
                                    _odooService.isAdmin) ...[
                                  const SizedBox(height: 16),
                                  ElevatedButton.icon(
                                    onPressed: _showAddClientDialog,
                                    icon: const Icon(Icons.add),
                                    label: const Text('Add First Customer'),
                                  ),
                                ],
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: _filteredClients.length,
                            itemBuilder: (context, index) {
                              final client = _filteredClients[index];
                              return Card(
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 16.0,
                                  vertical: 4.0,
                                ),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: const Color(0xFF1E88E5),
                                    child: Text(
                                      client.name.isNotEmpty
                                          ? client.name[0].toUpperCase()
                                          : 'C',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  title: Text(
                                    client.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      if (client.phone.isNotEmpty)
                                        Text(
                                          '📞 ${client.phone}',
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                      if (client.email.isNotEmpty)
                                        Text(
                                          '✉️ ${client.email}',
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                      if (client.city.isNotEmpty)
                                        Text(
                                          '📍 ${client.city}',
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                    ],
                                  ),
                                  trailing: const Icon(Icons.arrow_forward_ios),
                                  onTap: () => _showClientDetails(client),
                                ),
                              );
                            },
                          ),
                  ),
          ),
        ],
      ),
      floatingActionButton: _odooService.isAdmin
          ? FloatingActionButton(
              onPressed: _showAddClientDialog,
              backgroundColor: const Color(0xFF1E88E5),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
      bottomNavigationBar: const BottomNav(currentIndex: 2),
    );
  }
}
