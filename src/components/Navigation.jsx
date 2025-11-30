import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { getAccessToken, getCurrentUser, logout as logoutUser } from '@/lib/auth';
import { useEffect, useState } from 'react';
import { User, LogOut, Shield, ShoppingBag, Home } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export function Navigation() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
    
    // Listen for auth state changes
    const handleAuthChange = () => {
      checkAuth();
    };
    window.addEventListener('auth-state-changed', handleAuthChange);
    
    return () => {
      window.removeEventListener('auth-state-changed', handleAuthChange);
    };
  }, []);

  const checkAuth = async () => {
    const token = getAccessToken();
    if (token) {
      const userData = await getCurrentUser();
      if (userData) {
        setIsAuthenticated(true);
        setUser(userData);
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
      setIsAuthenticated(false);
      setUser(null);
      toast({
        title: "Logged out",
        description: "You have been logged out successfully",
      });
      navigate('/');
    } catch (error) {
      toast({
        title: "Logout failed",
        description: error.message || "Failed to logout",
        variant: "destructive",
      });
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield className="h-4 w-4" />;
      case 'seller':
        return <ShoppingBag className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'text-red-600';
      case 'seller':
        return 'text-blue-600';
      default:
        return 'text-green-600';
    }
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center space-x-2">
          <Shield className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            MedVerify
          </span>
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center space-x-4">
          <Link to="/" className="flex items-center space-x-1 text-sm font-medium text-muted-foreground hover:text-foreground">
            <Home className="h-4 w-4" />
            <span>Home</span>
          </Link>

          {isAuthenticated ? (
            <>
              {/* Dashboard Links based on role */}
              {user?.role === 'admin' && (
                <>
                  <Link to="/admin/dashboard">
                    <Button variant="ghost" size="sm">
                      <Shield className="h-4 w-4 mr-2" />
                      Admin Dashboard
                    </Button>
                  </Link>
                  <Link to="/admin/medicines">
                    <Button variant="ghost" size="sm">
                      <ShoppingBag className="h-4 w-4 mr-2" />
                      Medicines
                    </Button>
                  </Link>
                </>
              )}
              {user?.role === 'seller' && (
                <>
                  <Link to="/seller/dashboard">
                    <Button variant="ghost" size="sm">
                      <ShoppingBag className="h-4 w-4 mr-2" />
                      Seller Dashboard
                    </Button>
                  </Link>
                  <Link to="/seller/medicines">
                    <Button variant="ghost" size="sm">
                      <ShoppingBag className="h-4 w-4 mr-2" />
                      Medicines
                    </Button>
                  </Link>
                </>
              )}
              {user?.role === 'user' && (
                <>
                  <Link to="/user/dashboard">
                    <Button variant="ghost" size="sm">
                      <User className="h-4 w-4 mr-2" />
                      My Dashboard
                    </Button>
                  </Link>
                </>
              )}

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className={getRoleColor(user?.role)}>
                        {getRoleIcon(user?.role)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user?.email}</p>
                      <p className="text-xs leading-none text-muted-foreground capitalize">
                        {user?.role || 'user'}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Login
                </Button>
              </Link>
              <Link to="/register">
                <Button size="sm">
                  Register
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

