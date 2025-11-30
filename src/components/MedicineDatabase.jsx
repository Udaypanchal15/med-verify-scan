import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import {
  Search,
  Filter,
  Pill,
  Building,
  Calendar,
  ShieldCheck,
  AlertTriangle,
  Package,
  Loader,
  CheckCircle2
} from "lucide-react";
import { fetchMedicineInfo } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { getAuthHeader } from "@/lib/auth";

export const MedicineDatabase = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [medicines, setMedicines] = useState([]);
  const [medicineCategories, setMedicineCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const resultsPerPage = 12;

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  // Load seller's medicines on mount
  useEffect(() => {
    const loadSellerMedicines = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/seller/medicine`, {
          headers: getAuthHeader(),
        });

        if (response.ok) {
          const data = await response.json();
          const sellerMedicines = data.data || [];
          setMedicines(sellerMedicines);

          // Extract unique categories from seller's medicines
          const categories = [...new Set(sellerMedicines.map(m => m.category).filter(Boolean))];
          setMedicineCategories(categories.sort());
        } else {
          toast({
            title: "Error",
            description: "Failed to load medicines",
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error("Error fetching medicines:", error);
        toast({
          title: "Error",
          description: "Failed to load medicines",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadSellerMedicines();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Error",
        description: "Please enter a medicine name to search.",
        variant: "destructive",
      });
      return;
    }

    setIsSearching(true);
    setCurrentPage(1);

    try {
      const data = await fetchMedicineInfo(searchQuery);

      if (data.error) {
        toast({
          title: "Not Found",
          description: data.error,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Medicine Found ✅",
          description: `Information retrieved for ${data.medicine}`,
        });
      }
    } catch (error) {
      console.error("Error fetching medicine:", error);
      toast({
        title: "Error",
        description: "Failed to fetch medicine info.",
        variant: "destructive",
      });
    } finally {
      setIsSearching(false);
    }
  };

  // Filter seller's medicines by category and search query
  const filteredMedicines = medicines.filter((m) => {
    const matchesCategory = !selectedCategory || selectedCategory === "all" || m.category === selectedCategory;
    const q = searchQuery.trim().toLowerCase();
    const matchesQuery = !q ||
      m.name.toLowerCase().includes(q) ||
      m.batch_no.toLowerCase().includes(q) ||
      (m.manufacturer && m.manufacturer.toLowerCase().includes(q)) ||
      (m.strength && m.strength.toLowerCase().includes(q));
    return matchesCategory && matchesQuery;
  });

  const effectiveResults = filteredMedicines;

  const paginatedResults = effectiveResults.slice(
    (currentPage - 1) * resultsPerPage,
    currentPage * resultsPerPage
  );

  const totalPages = Math.ceil(effectiveResults.length / resultsPerPage);

  const getStatusBadge = (status) => {
    switch (status) {
      case "approved":
        return (
          <Badge className="bg-green-100 text-green-700 border-green-200">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Approved
          </Badge>
        );
      case "pending":
        return (
          <Badge className="bg-yellow-100 text-yellow-700 border-yellow-200">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case "rejected":
        return (
          <Badge className="bg-red-100 text-red-700 border-red-200">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Rejected
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "approved":
        return <ShieldCheck className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    }
  };

  return (
    <section id="database" className="py-20 bg-secondary/20">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Your Medicine Database</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            View and manage all medicines registered by you in our system.
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <Card className="max-w-2xl mx-auto p-12 text-center">
            <div className="flex items-center justify-center gap-3">
              <Loader className="h-6 w-6 animate-spin text-primary" />
              <p className="text-muted-foreground">Loading your medicines...</p>
            </div>
          </Card>
        )}

        {/* Search Interface */}
        {!loading && (
        <Card className="max-w-5xl mx-auto p-8 mb-8">
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by medicine name, active ingredient, manufacturer..."
                  className="pl-10 py-6 text-lg"
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
              <Select
                value={selectedCategory}
                onValueChange={(value) => {
                  setSelectedCategory(value);
                  setSearchResults([]);
                  setCurrentPage(1);
                }}
              >
                <SelectTrigger className="w-full md:w-48 py-6">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {medicineCategories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={handleSearch}
                disabled={isSearching}
                className="px-8 py-6 bg-gradient-to-r from-primary to-accent min-w-32"
              >
                {isSearching ? "Searching..." : "Search"}
              </Button>
            </div>

            <div className="flex gap-2 flex-wrap">
              {medicineCategories.length > 0 ? (
                medicineCategories.map((category) => (
                  <Button
                    key={category}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedCategory(category);
                      setCurrentPage(1);
                    }}
                  >
                    <Pill className="mr-1 h-3 w-3" />
                    {category}
                  </Button>
                ))
              ) : null}
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedCategory("");
                  setCurrentPage(1);
                }}
              >
                <Package className="mr-1 h-3 w-3" />
                Show All
              </Button>
            </div>
          </div>
        </Card>
        )}

        {/* No Results */}
        {!loading && effectiveResults.length === 0 &&
          (searchQuery || selectedCategory) && (
            <Card className="max-w-2xl mx-auto p-12 text-center">
              <div className="w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                No medicines found
              </h3>
              <p className="text-muted-foreground">
                Try searching with different keywords or select a different category.
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedCategory("");
                  setCurrentPage(1);
                }}
                className="mt-4"
              >
                Clear filters
              </Button>
            </Card>
          )}
            <div className="mb-6 flex justify-between items-center">
              <div>
                <h3 className="text-2xl font-semibold mb-2">Search Results</h3>
                <p className="text-muted-foreground">
                  {effectiveResults.length} medicine(s) found • Showing{" "}
                  {paginatedResults.length} results
                </p>
              </div>
              <Badge variant="outline" className="px-3 py-1">
                Page {currentPage} of {totalPages}
              </Badge>
            </div>

        {/* Search Results */}
        {!loading && effectiveResults.length > 0 && (
          <div className="max-w-7xl mx-auto">
            <div className="mb-6 flex justify-between items-center">
              <div>
                <h3 className="text-2xl font-semibold mb-2">Your Medicines</h3>
                <p className="text-muted-foreground">
                  {effectiveResults.length} medicine(s) found • Showing{" "}
                  {paginatedResults.length} results
                </p>
              </div>
              <Badge variant="outline" className="px-3 py-1">
                Page {currentPage} of {totalPages}
              </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {paginatedResults.map((medicine) => (
                <Card
                  key={medicine.id}
                  className="p-6 hover:shadow-card transition-all duration-300 group"
                >
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="text-lg font-semibold group-hover:text-primary transition-colors">
                          {medicine.name}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          Batch: {medicine.batch_no}
                        </p>
                      </div>
                      {getStatusBadge(medicine.approval_status)}
                    </div>

                    <Badge variant="secondary" className="w-fit">
                      {medicine.category}
                    </Badge>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <label className="font-medium text-muted-foreground text-xs">
                          Strength
                        </label>
                        <p className="font-medium">{medicine.strength || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="font-medium text-muted-foreground text-xs">
                          Dosage
                        </label>
                        <p className="font-medium">{medicine.dosage || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="font-medium text-muted-foreground text-xs">
                          Stock
                        </label>
                        <p className={`font-medium ${medicine.stock_quantity === 0 ? 'text-red-600' : medicine.stock_quantity < 10 ? 'text-amber-600' : 'text-green-600'}`}>
                          {medicine.stock_quantity || 0}
                        </p>
                      </div>
                      <div>
                        <label className="font-medium text-muted-foreground text-xs">
                          Delivery
                        </label>
                        <p className="font-medium text-sm capitalize">{medicine.delivery_status || 'N/A'}</p>
                      </div>
                    </div>

                    {medicine.manufacturer && (
                      <div className="flex items-center gap-2 p-3 bg-muted/30 rounded-lg">
                        <Building className="h-4 w-4 text-primary shrink-0" />
                        <span className="font-medium text-sm truncate">
                          {medicine.manufacturer}
                        </span>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-sm pt-2 border-t border-border/50">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-3 w-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          Exp: {medicine.expiry_date ? new Date(medicine.expiry_date).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                      {getStatusIcon(medicine.approval_status)}
                    </div>

                    {medicine.description && (
                      <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                        {medicine.description}
                      </p>
                    )}
                  </div>
                </Card>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <Button
                  variant="outline"
                  onClick={() =>
                    setCurrentPage((prev) => Math.max(prev - 1, 1))
                  }
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                  (page) => (
                    <Button
                      key={page}
                      variant={page === currentPage ? "default" : "outline"}
                      onClick={() => setCurrentPage(page)}
                      className="w-10"
                    >
                      {page}
                    </Button>
                  )
                )}
                <Button
                  variant="outline"
                  onClick={() =>
                    setCurrentPage((prev) =>
                      Math.min(prev + 1, totalPages)
                    )
                  }
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};
