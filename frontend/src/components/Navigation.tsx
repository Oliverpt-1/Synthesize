import React from 'react';
import { Menu, User, Book, CreditCard, Settings, LogOut } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

const Navigation: React.FC = () => {
  return (
    <nav className="absolute top-0 left-0 right-0 p-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger className="p-2 hover:bg-primary-50 rounded-lg transition-colors">
            <Menu className="w-5 h-5 text-gray-700" />
          </DropdownMenu.Trigger>
          
          <DropdownMenu.Portal>
            <DropdownMenu.Content className="bg-white rounded-lg shadow-lg p-2 min-w-[200px] animate-slideDown">
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 hover:bg-primary-50 rounded-md cursor-pointer text-gray-700">
                <Book className="w-4 h-4" />
                <span>My Audiobooks</span>
              </DropdownMenu.Item>
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 hover:bg-primary-50 rounded-md cursor-pointer text-gray-700">
                <CreditCard className="w-4 h-4" />
                <span>Billing</span>
              </DropdownMenu.Item>
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 hover:bg-primary-50 rounded-md cursor-pointer text-gray-700">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="h-px bg-gray-200 my-2" />
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 hover:bg-primary-50 rounded-md cursor-pointer text-gray-700">
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <div className="flex items-center gap-2">
          <div className="text-right mr-3">
            <p className="text-sm font-medium text-gray-900">John Doe</p>
            <p className="text-xs text-gray-500">john@example.com</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <User className="w-5 h-5 text-primary-600" />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;