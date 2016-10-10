#!/usr/bin/env python3

import sys
import shutil

#if you didn't expand pokemon before, do not touch those values
old_pokes = 412
old_pokes_sprite = 440
old_pokes_dex = 386

#those values should be configured according to user
free_space = 0xFA4000
new_pokes = 1000 + 53 #amount of all pokes you want, ignore that 53, it's for limbo and used up slots
dex_pokes = 999  + 1 #amount of pokes you want to have in national dex, ignore that 1
clear_repointed_data = True
Movesets_repoint = True
TmHmComp_repoint = True
MoveTutorComp_repoint = True
evos_per_entry = 5
rom_name = 'expans.gba'
new_rom_name = 'new.gba'

table_names = ["base_stats", "poke_front_img", "poke_back_img", "poke_sprite_pal", "shiny_sprite_pal", "icon_img", "icon_pal", "poke_names", "tm_hm_comp_table", "move_tutor_table", "dex_table", "evo_table", "enymyyTable", "playeryTable", "learnset_table", "front_animation_table", "anim_delay_table", "footprint_table", "crytable1", "crytable2", "altitude_table", "auxialary_cry_table", "nationaldex_table", "hoenn_to_national_table", "hoenn_dex_table", "back_anim_table", "frame_control_table"]
table_ptrs = [0x0001BC, 0x000128, 0x00012C, 0x000130, 0x000134, 0x000138, 0x00013C, 0x000144, 0x06E060, 0x1B2390, 0x0BFA20, 0x06D140, 0x0A5F54, 0x0A5EBC, 0x06E3B4, 0x06EE7C, 0x06EDDC, 0x0C0DBC, 0x0A35EC, 0x0A35DC, 0x0A5FF4, 0x06D534, 0x06D448, 0x06D494, 0x06D3FC, 0x17F488, 0x05E7BC]
sizeofs = [0x1C, 8, 8, 8, 8, 4, 1, 11, 8, 4, 0x20, evos_per_entry * 8, 4, 4, 4, 1, 1, 4, 0xC, 0xC, 1, 2, 2, 2, 2, 1, 4]
to_repoint = [True, True, True, True, True, True, True, True, TmHmComp_repoint, MoveTutorComp_repoint, True, True, True, True, Movesets_repoint, True, True, True, True, True, True, True, True, True, True, True, True]

no_of_names = len(table_names)
no_of_tables = len(table_ptrs)
no_of_sizeofs = len(sizeofs)
no_of_to_repoints = len(to_repoint)

def find_offset_to_put(rom, needed_bytes):
	offset = free_space
	found_bytes = 0
	while (found_bytes < needed_bytes):
		for i in range (0, needed_bytes):
			rom.seek(offset + i)
			byte = rom.read(1)
			if (byte):
				if (byte != b'\xFF'):
					offset += i + 1
					found_bytes = 0
					break
				found_bytes += 1
			else:
				return 0
	return offset

def get_oldtable_address(rom, tableID):
	if (tableID < no_of_tables):
		ptr = table_ptrs[tableID]
		rom.seek(ptr)
		table_ptr = rom.read(4)
		return int.from_bytes(table_ptr, byteorder = 'little') - 0x08000000
	return 0
	
def update_ptrs(rom, ptr, tableID):
	name = table_names[tableID]
	if name == "base_stats":
		rom.seek(0x06EB7C) #item 1
		rom.write((ptr + 0xC).to_bytes(4, byteorder = 'little'))
		rom.seek(0x06EBA0) #item 2
		rom.write((ptr + 0xE).to_bytes(4, byteorder = 'little'))
	elif name == "crytable1":
		rom.seek(0x0A3610)
		rom.write((ptr + 0x600).to_bytes(4, byteorder = 'little'))
		rom.seek(0x0A3634)
		rom.write((ptr + 0xC00).to_bytes(4, byteorder = 'little'))
		rom.seek(0x0A3670)
		rom.write((ptr + 0x1200).to_bytes(4, byteorder = 'little'))
	elif name == "crytable2":
		rom.seek(0x0A3600)
		rom.write((ptr + 0x600).to_bytes(4, byteorder = 'little'))
		rom.seek(0x0A3624)
		rom.write((ptr + 0xC00).to_bytes(4, byteorder = 'little'))
		rom.seek(0x0A3648)
		rom.write((ptr + 0x1200).to_bytes(4, byteorder = 'little'))
	elif name == "anim_delay_table":
		rom.seek(0x034BFE)
		rom.write((0xE007).to_bytes(2, byteorder = 'little'))
		rom.seek(0x0A5FE)
		rom.write((0xE003).to_bytes(2, byteorder = 'little'))
	elif name == "altitude_table":
		rom.seek(0x0A5F82)
		rom.write((0xE003).to_bytes(2, byteorder = 'little'))
		rom.seek(0x0A5EB6)
		rom.write((0xE003).to_bytes(2, byteorder = 'little'))
	elif name == "shiny_sprite_pal":
		rom.seek(0x06E750)
		rom.write((0xE004).to_bytes(2, byteorder = 'little'))
	elif name == "poke_back_img":
		rom.seek(0x0346D6)
		rom.write((0xE007).to_bytes(2, byteorder = 'little'))
		rom.seek(0x034AC2)
		rom.write((0xE007).to_bytes(2, byteorder = 'little'))
	elif name == "poke_front_img":
		rom.seek(0x0346D2)
		rom.write((80).to_bytes(1, byteorder = 'little'))
		rom.seek(0x034BFA)
		rom.write((80).to_bytes(1, byteorder = 'little'))
	elif name == "nationaldex_table":
		offset = ptr - 0x08000000
		for i in range(0, 386):
			rom.seek(offset)
			dex_no = int.from_bytes(rom.read(2), byteorder = 'little')
			if (dex_no > 386):
				rom.seek(offset)
				rom.write((0x0).to_bytes(2, byteorder = 'little'))
			offset += 2
	oldptr = (get_oldtable_address(rom, tableID) + 0x08000000).to_bytes(4, byteorder = 'little')
	newptr = ptr.to_bytes(4, byteorder = 'little')
	rom.seek(0x0)
	copy = rom.read(0x1E8000)
	copy = copy.replace(oldptr, newptr)
	rom.seek(0x0)
	rom.write(copy)

def get_no_of_old_slots(tableID):
	name = table_names[tableID]
	if name == "poke_back_img" or name == "poke_front_img" or name == "shiny_sprite_pal" or name == "poke_sprite_pal" or name == "icon_img" or name == "icon_pal" or name == "enemyyTable" or name == "playeryTable" or name == "frame_control_table":
		return old_pokes_sprite
	elif name == "dex_table":
		return old_pokes_dex + 1
	elif name == "front_animation_table" or name == "anim_delay_table" or name == "hoenn_dex_table" or name == "nationaldex_table" or name == "hoenn_to_national_table":
		return old_pokes - 1
	elif name == "crytable1" or name == "crytable2":
		return old_pokes + 2
	elif name == "auxialary_cry_table":
		return 136
	return old_pokes

def repoint_table(rom, offset, tableID):
	table_ptr = get_oldtable_address(rom, tableID)
	name = table_names[tableID]
	if table_ptr:
		sizeof = sizeofs[tableID]
		old_slots = get_no_of_old_slots(tableID)
		needed_old = old_slots * sizeof
		needed_new = (new_pokes - old_slots) * sizeof
		#get empty slot to copy
		rom.seek(table_ptr + sizeof)
		empty_slot = rom.read(sizeof)
		# copy old data
		rom.seek(table_ptr)
		to_copy = rom.read(needed_old)
		#align 4
		while (offset % 4) != 0:
			offset += 1
		rom.seek(offset)
		rom.write(to_copy)
		if (clear_repointed_data == True):
			rom.seek(table_ptr)
			for i in range(0, needed_old):
				rom.write(b'\xFF')
		update_ptrs(rom, offset + 0x08000000, tableID)
		offset += needed_old
		rom.seek(offset)
		#append unowns
		if old_slots < 440:
			for i in range(old_slots, 440):
				if (name == "poke_names"):
					rom.write((0xBB + (440 - i)).to_bytes(1, byteorder = 'little'))
					rom.write((0x0).to_bytes(9, byteorder = 'little'))
					rom.write((0xFF).to_bytes(1, byteorder = 'little'))
				elif name == "nationaldex_table":
					rom.write((201).to_bytes(sizeof, byteorder = 'little'))
				else:
					rom.write(empty_slot)
				offset += sizeof
		# write new data for empty slots
		new_slots = new_pokes
		for i in range(0, (new_slots - 440)):
			if name == "hoenn_dex_table" or name == "hoenn_to_national_table":
				rom.write((440 + i).to_bytes(sizeof, byteorder = 'little'))
			elif name == "nationaldex_table":
				rom.write((387 + i).to_bytes(sizeof, byteorder = 'little'))
			else:
				rom.write(empty_slot)
			offset += sizeof
	return offset

def dex_related_bytechanges(rom):	
	max_pokes = (dex_pokes - 1).to_bytes(4, byteorder = 'little')
	rom.seek(0x0BCEE4)
	rom.write(max_pokes)
	rom.seek(0x0BCFAC)
	rom.write(max_pokes)
	rom.seek(0x0BD0C4)
	rom.write(max_pokes)
	rom.seek(0x0C080C)
	if dex_pokes > 999:
		rom.write((999).to_bytes(4, byteorder = 'little'))
	else:
		rom.write(max_pokes)

shutil.copyfile(rom_name, new_rom_name)
with open('BPEE0.gba', 'rb+') as rom:
	if (no_of_sizeofs != no_of_tables or no_of_sizeofs != no_of_to_repoints or no_of_names != no_of_sizeofs):
		print("Tables don't match.")
		print(no_of_names, " ", no_of_sizeofs, " ", no_of_tables, " ", no_of_to_repoints)
		sys.exit(1)
	if (new_pokes <= old_pokes):
		print("Amount of new pokemon must be higher than the current one.")
		sys.exit(1)
	needed_bytes = 0
	for i in range(0, no_of_tables):
		needed_bytes += (old_pokes * sizeofs[i])
	offset = find_offset_to_put(rom, needed_bytes)
	if (offset == 0):
		print("Not enough free space.")
		sys.exit(1)
	for i in range(0, no_of_tables):
		if (to_repoint[i] == True):
			offset = repoint_table(rom, offset, i)
	dex_related_bytechanges(rom)
	rom.close()
