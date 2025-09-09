-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 09, 2025 at 03:07 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `evidencija`
--

-- --------------------------------------------------------

--
-- Table structure for table `korisnici`
--

CREATE TABLE `korisnici` (
  `id` int(11) NOT NULL,
  `ime` varchar(50) NOT NULL,
  `prezime` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `tip_korisnika` enum('korisnik','admin') DEFAULT 'korisnik',
  `datum_kreiranja` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `korisnici`
--

INSERT INTO `korisnici` (`id`, `ime`, `prezime`, `email`, `password`, `tip_korisnika`, `datum_kreiranja`) VALUES
(1, 'Admin', 'Adminovic', 'admin@admin.com', '$pbkdf2:sha256:600000$h4RkLm...hash_ovde...', 'admin', '2025-09-08 18:28:55'),
(2, 'Andrija', 'Djordjev', 'andrijadjordjev1@gmail.com', 'scrypt:32768:8:1$37Nh6zwnRWQXzdHH$4b8ca40cb953c2f89681c94c22a3c09660c8ba01cdd5bf36d3ba161c5df6b969a78c77de44546e85af4cb822dfdca3e44d3eecf98b124c90948ebf119e8f205b', 'admin', '2025-09-08 16:30:28'),
(3, 'Filip', 'Stojkovic', 'stojkovic05@gmail.com', 'scrypt:32768:8:1$1pMnj7tc4HiGBEq9$e1e77dd8a0a05369774c17eb912e7a17400b9e6d817c6fd6093740452f376e84be25181787b2eceb6c99da78eb5008278be1c20c3c19644efb93530a5c6093c7', 'korisnik', '2025-09-08 16:35:39');

-- --------------------------------------------------------

--
-- Table structure for table `rezervacije`
--

CREATE TABLE `rezervacije` (
  `id` int(11) NOT NULL,
  `korisnik_id` int(11) NOT NULL,
  `termin_id` int(11) NOT NULL,
  `datum_rezervacije` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('aktivna','otkazana','zavrsena') DEFAULT 'aktivna',
  `napomena` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rezervacije`
--

INSERT INTO `rezervacije` (`id`, `korisnik_id`, `termin_id`, `datum_rezervacije`, `status`, `napomena`) VALUES
(1, 2, 1, '2025-09-08 16:35:11', 'otkazana', NULL),
(2, 2, 2, '2025-09-08 16:35:24', 'aktivna', NULL),
(3, 3, 1, '2025-09-08 16:35:53', 'aktivna', NULL),
(4, 3, 4, '2025-09-08 16:36:34', 'aktivna', NULL),
(6, 2, 5, '2025-09-08 16:44:35', 'aktivna', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `termini`
--

CREATE TABLE `termini` (
  `id` int(11) NOT NULL,
  `naziv` varchar(100) NOT NULL,
  `opis` text DEFAULT NULL,
  `datum` date NOT NULL,
  `vreme` time NOT NULL,
  `trajanje` int(11) NOT NULL,
  `max_korisnika` int(11) NOT NULL,
  `kreirao_id` int(11) DEFAULT NULL,
  `status` enum('dostupan','zauzet','otkazan') DEFAULT 'dostupan',
  `datum_kreiranja` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `termini`
--

INSERT INTO `termini` (`id`, `naziv`, `opis`, `datum`, `vreme`, `trajanje`, `max_korisnika`, `kreirao_id`, `status`, `datum_kreiranja`) VALUES
(1, 'Frizura', 'Srednji FADE', '2025-09-10', '12:00:00', 45, 3, 2, 'dostupan', '2025-09-08 16:31:36'),
(2, 'Pranje i feniranje kose', 'Pranje kose i feniranje', '2025-09-11', '11:00:00', 30, 2, 2, 'dostupan', '2025-09-08 16:32:04'),
(4, 'Šišanje i sređivanje brade', 'Šišanje na frizuru po želji + brijanje/sređivanje brade', '2025-09-13', '09:00:00', 60, 2, 2, 'dostupan', '2025-09-08 16:34:51'),
(5, 'Sređivanje brade', 'Sredjivanje brade po želji', '2025-09-11', '12:00:00', 30, 1, 2, 'dostupan', '2025-09-08 16:44:19'),
(6, 'Brijanje', 'Brijanje brade', '2025-09-11', '12:00:00', 20, 1, 2, 'dostupan', '2025-09-08 16:52:39');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `korisnici`
--
ALTER TABLE `korisnici`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `rezervacije`
--
ALTER TABLE `rezervacije`
  ADD PRIMARY KEY (`id`),
  ADD KEY `korisnik_id` (`korisnik_id`),
  ADD KEY `termin_id` (`termin_id`);

--
-- Indexes for table `termini`
--
ALTER TABLE `termini`
  ADD PRIMARY KEY (`id`),
  ADD KEY `kreirao_id` (`kreirao_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `korisnici`
--
ALTER TABLE `korisnici`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `rezervacije`
--
ALTER TABLE `rezervacije`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `termini`
--
ALTER TABLE `termini`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `rezervacije`
--
ALTER TABLE `rezervacije`
  ADD CONSTRAINT `rezervacije_ibfk_1` FOREIGN KEY (`korisnik_id`) REFERENCES `korisnici` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `rezervacije_ibfk_2` FOREIGN KEY (`termin_id`) REFERENCES `termini` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `termini`
--
ALTER TABLE `termini`
  ADD CONSTRAINT `termini_ibfk_1` FOREIGN KEY (`kreirao_id`) REFERENCES `korisnici` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
