/**
 * House3DWorld — Full 3D Interactive Construction RPG World for Tezz-Mindz Game Engine.
 * Features 5 distinct sequential in-world interactable stations with 3D waypoint beacons and locked-state indicators.
 */
class House3DWorld {
  constructor(containerId, player) {
    this.container = document.getElementById(containerId);
    this.player = player;
    this.currentStage = 0;
    this.interactables = [];
    this.nearbyNPC = null;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    // Stage meshes
    this.foundationMesh = null;
    this.wallsGroup = null;
    this.roofGroup = null;
    this.villaGroup = null;
    this.waypointBeacon = null;

    if (this.container && window.THREE) {
      this.init3D();
    }
  }

  init3D() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xBAE6FD);
    this.scene.fog = new THREE.FogExp2(0xBAE6FD, 0.02);

    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    this.camera.position.set(0, 14, 18);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // Setup World
    this.setupLighting();
    this.buildEnvironment();
    this.buildConstructionPlot();
    this.buildLevelStations();
    this.createWaypointBeacon();

    // Spawn Player Character
    if (window.GameCharacter) {
      this.character = new GameCharacter(this.scene, this.camera);
    }

    this.initInteractionListeners();
    window.addEventListener('resize', () => this.onResize());
    this.animate();
  }

  setupLighting() {
    const hemi = new THREE.HemisphereLight(0xffffff, 0x86efac, 0.85);
    this.scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfffaed, 1.25);
    sun.position.set(16, 28, 14);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    sun.shadow.bias = -0.0005;
    this.scene.add(sun);
  }

  buildEnvironment() {
    // 3D Grass Island
    const grassGeo = new THREE.CylinderGeometry(16, 16.5, 1.2, 36);
    const grassMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8 });
    this.groundMesh = new THREE.Mesh(grassGeo, grassMat);
    this.groundMesh.position.y = -0.6;
    this.groundMesh.receiveShadow = true;
    this.scene.add(this.groundMesh);

    // Dirt Underlayer
    const dirtGeo = new THREE.CylinderGeometry(16.5, 15, 3, 36);
    const dirtMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.9 });
    const dirtMesh = new THREE.Mesh(dirtGeo, dirtMat);
    dirtMesh.position.y = -2.7;
    this.scene.add(dirtMesh);

    // Pathways connecting all stations
    const pathMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.7 });
    
    const roadX = new THREE.Mesh(new THREE.BoxGeometry(22, 0.05, 2.6), pathMat);
    roadX.position.set(0, 0.03, 3);
    roadX.receiveShadow = true;
    this.scene.add(roadX);

    const roadZ = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.05, 22), pathMat);
    roadZ.position.set(0, 0.03, 0);
    roadZ.receiveShadow = true;
    this.scene.add(roadZ);

    // Surrounding Trees
    const treeMat = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.7 });
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.9 });
    const treePositions = [[-12, -7], [12, -7], [-12, 6], [12, 6], [5, -12], [-5, -12]];

    treePositions.forEach(([tx, tz]) => {
      const tree = new THREE.Group();
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 1.6, 8), trunkMat);
      trunk.position.y = 0.8;
      trunk.castShadow = true;
      tree.add(trunk);

      const leaves = new THREE.Mesh(new THREE.ConeGeometry(1.6, 3.2, 8), treeMat);
      leaves.position.y = 2.8;
      leaves.castShadow = true;
      tree.add(leaves);

      tree.position.set(tx, 0, tz);
      this.scene.add(tree);
    });
  }

  buildConstructionPlot() {
    this.plotGroup = new THREE.Group();

    const postMat = new THREE.MeshStandardMaterial({ color: 0x92400e, roughness: 0.8 });
    const postGeo = new THREE.CylinderGeometry(0.12, 0.12, 1.4, 8);
    const postCoords = [[-3.5, -3.5], [3.5, -3.5], [3.5, 3.5], [-3.5, 3.5]];

    postCoords.forEach(([px, pz]) => {
      const p = new THREE.Mesh(postGeo, postMat);
      p.position.set(px, 0.7, pz);
      p.castShadow = true;
      this.plotGroup.add(p);
    });

    this.frontRibbon = new THREE.Mesh(new THREE.BoxGeometry(7, 0.1, 0.05), new THREE.MeshStandardMaterial({ color: 0xfacc15 }));
    this.frontRibbon.position.set(0, 0.9, 3.5);
    this.plotGroup.add(this.frontRibbon);

    // "FOR SALE" Billboard
    this.forSaleSign = new THREE.Group();
    const signPole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.4, 8), postMat);
    signPole.position.set(0, 1.2, 3.4);
    this.forSaleSign.add(signPole);

    const signBoard = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1.6, 0.15), new THREE.MeshStandardMaterial({ color: 0x1e1b4b }));
    signBoard.position.set(0, 2.2, 3.4);
    signBoard.castShadow = true;
    this.forSaleSign.add(signBoard);
    this.plotGroup.add(this.forSaleSign);

    // 3D Foundation (Stage 2)
    this.foundationMesh = new THREE.Mesh(
      new THREE.BoxGeometry(5.6, 0.5, 5.2),
      new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.8 })
    );
    this.foundationMesh.position.set(0, 0.25, 0);
    this.foundationMesh.receiveShadow = true;
    this.foundationMesh.castShadow = true;
    this.foundationMesh.visible = false;
    this.plotGroup.add(this.foundationMesh);

    // 3D Brick Walls & Windows (Stage 3)
    this.wallsGroup = new THREE.Group();
    const wallBody = new THREE.Mesh(
      new THREE.BoxGeometry(5.2, 3.0, 4.8),
      new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.7 })
    );
    wallBody.position.set(0, 2.0, 0);
    wallBody.castShadow = true;
    this.wallsGroup.add(wallBody);

    const door = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.0, 0.15), new THREE.MeshStandardMaterial({ color: 0x9a3412 }));
    door.position.set(0, 1.5, 2.42);
    this.wallsGroup.add(door);

    const winMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.5, roughness: 0.1 });
    const winL = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.0, 0.1), winMat);
    winL.position.set(-1.6, 2.2, 2.42);
    this.wallsGroup.add(winL);
    const winR = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.0, 0.1), winMat);
    winR.position.set(1.6, 2.2, 2.42);
    this.wallsGroup.add(winR);

    this.wallsGroup.visible = false;
    this.plotGroup.add(this.wallsGroup);

    // 3D Roof (Stage 4)
    this.roofGroup = new THREE.Group();
    const roof = new THREE.Mesh(
      new THREE.ConeGeometry(4.4, 2.2, 4),
      new THREE.MeshStandardMaterial({ color: 0xea580c, roughness: 0.6 })
    );
    roof.position.set(0, 4.6, 0);
    roof.rotation.y = Math.PI / 4;
    roof.castShadow = true;
    this.roofGroup.add(roof);

    const chim = new THREE.Mesh(new THREE.BoxGeometry(0.7, 1.6, 0.7), new THREE.MeshStandardMaterial({ color: 0x78350f }));
    chim.position.set(1.4, 5.0, -0.8);
    chim.castShadow = true;
    this.roofGroup.add(chim);

    this.roofGroup.visible = false;
    this.plotGroup.add(this.roofGroup);

    // 3D Complete Villa Accents (Stage 5)
    this.villaGroup = new THREE.Group();
    const nameplate = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.08), new THREE.MeshStandardMaterial({ color: 0xfde047, metalness: 0.8 }));
    nameplate.position.set(0, 2.8, 2.45);
    this.villaGroup.add(nameplate);

    this.villaGroup.visible = false;
    this.plotGroup.add(this.villaGroup);

    // Bulldozer
    this.buildBulldozer();

    this.scene.add(this.plotGroup);
  }

  buildBulldozer() {
    this.bulldozer = new THREE.Group();
    const yellowMat = new THREE.MeshStandardMaterial({ color: 0xeab308 });
    const blackMat = new THREE.MeshStandardMaterial({ color: 0x1e293b });

    const body = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.9, 1.3), yellowMat);
    body.position.y = 0.7;
    body.castShadow = true;
    this.bulldozer.add(body);

    const blade = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.8, 1.6), blackMat);
    blade.position.set(1.2, 0.45, 0);
    this.bulldozer.add(blade);

    this.bulldozer.position.set(7, 0, -2);
    this.bulldozer.rotation.y = -Math.PI / 2;
    this.scene.add(this.bulldozer);
  }

  buildLevelStations() {
    // ── STATION 1: MR. SHARMA (LAND BROKER) at (-6, 0, 3) ───────────────────
    this.brokerNPC = new THREE.Group();
    const kioskMat = new THREE.MeshStandardMaterial({ color: 0x4f46e5 });
    const desk = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.0, 1.1), new THREE.MeshStandardMaterial({ color: 0x92400e }));
    desk.position.set(-6, 0.5, 3);
    this.brokerNPC.add(desk);

    const umbrella = new THREE.Mesh(new THREE.ConeGeometry(1.8, 0.8, 8), new THREE.MeshStandardMaterial({ color: 0xfacc15 }));
    umbrella.position.set(-6, 3.0, 2.4);
    this.brokerNPC.add(umbrella);

    const brokerBody = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.85, 0.35), kioskMat);
    brokerBody.position.set(-6, 1.1, 1.8);
    this.brokerNPC.add(brokerBody);

    const brokerHead = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.38), new THREE.MeshStandardMaterial({ color: 0xffdbac }));
    brokerHead.position.set(-6, 1.7, 1.8);
    this.brokerNPC.add(brokerHead);

    this.npcRightArm = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.55, 0.16), kioskMat);
    this.npcRightArm.position.set(-5.55, 1.3, 1.8);
    this.brokerNPC.add(this.npcRightArm);

    this.scene.add(this.brokerNPC);

    this.interactables.push({
      id: 'level_1_broker',
      name: 'Mr. Sharma (Land Broker)',
      position: new THREE.Vector3(-6, 0, 2.5),
      radius: 3.8,
      levelNum: 1,
      onInteract: () => this.openStation(1)
    });

    // ── STATION 2: CONCRETE MIXER DEPOT at (-6, 0, -4) ──────────────────────
    const mixerStation = new THREE.Group();
    const mixerDrum = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 1.8, 12), new THREE.MeshStandardMaterial({ color: 0x0284c7 }));
    mixerDrum.rotation.z = Math.PI / 3;
    mixerDrum.position.set(-6, 1.2, -4);
    mixerStation.add(mixerDrum);

    const mixerCab = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.2, 1.4), new THREE.MeshStandardMaterial({ color: 0xeab308 }));
    mixerCab.position.set(-4.5, 0.9, -4);
    mixerStation.add(mixerCab);
    this.scene.add(mixerStation);

    this.interactables.push({
      id: 'level_2_mixer',
      name: 'Foundation Mixer Depot',
      position: new THREE.Vector3(-5.5, 0, -4),
      radius: 3.8,
      levelNum: 2,
      onInteract: () => this.openStation(2)
    });

    // ── STATION 3: MATERIAL CRANE at (6, 0, -4) ─────────────────────────────
    const craneStation = new THREE.Group();
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 5, 8), new THREE.MeshStandardMaterial({ color: 0xfacc15 }));
    tower.position.set(6, 2.5, -4);
    craneStation.add(tower);

    const arm = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.2, 0.2), new THREE.MeshStandardMaterial({ color: 0xfacc15 }));
    arm.position.set(4.5, 4.9, -4);
    craneStation.add(arm);
    this.scene.add(craneStation);

    this.interactables.push({
      id: 'level_3_crane',
      name: 'Material Crane Console',
      position: new THREE.Vector3(5.5, 0, -4),
      radius: 3.8,
      levelNum: 3,
      onInteract: () => this.openStation(3)
    });

    // ── STATION 4: SUPPLIER MARKETPLACE at (6, 0, 3) ────────────────────────
    const marketStation = new THREE.Group();
    const table = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.9, 1.2), new THREE.MeshStandardMaterial({ color: 0x78350f }));
    table.position.set(6, 0.45, 3);
    marketStation.add(table);

    const crates = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), new THREE.MeshStandardMaterial({ color: 0xea580c }));
    crates.position.set(6, 1.3, 3);
    marketStation.add(crates);
    this.scene.add(marketStation);

    this.interactables.push({
      id: 'level_4_market',
      name: 'Supplier Marketplace Scale',
      position: new THREE.Vector3(6, 0, 3),
      radius: 3.8,
      levelNum: 4,
      onInteract: () => this.openStation(4)
    });

    // ── STATION 5: CHIEF ARCHITECT at (0, 0, 11) ────────────────────────────
    const architectStation = new THREE.Group();
    const archDesk = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.9, 1.2), new THREE.MeshStandardMaterial({ color: 0x312e81 }));
    archDesk.position.set(0, 0.45, 11);
    architectStation.add(archDesk);

    const blueprint = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.05, 0.9), new THREE.MeshStandardMaterial({ color: 0x38bdf8 }));
    blueprint.position.set(0, 0.95, 11);
    architectStation.add(blueprint);
    this.scene.add(architectStation);

    this.interactables.push({
      id: 'level_5_architect',
      name: 'Chief Architect Office',
      position: new THREE.Vector3(0, 0, 11),
      radius: 3.0,
      levelNum: 5,
      onInteract: () => this.openStation(5)
    });
  }

  createWaypointBeacon() {
    this.waypointBeacon = new THREE.Group();
    
    // Glowing Arrow Cone pointing down
    const coneGeo = new THREE.ConeGeometry(0.5, 1.0, 16);
    const coneMat = new THREE.MeshBasicMaterial({ color: 0xFDE047 });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.rotation.x = Math.PI; // Point down
    cone.position.y = 4.2;
    this.waypointBeacon.add(cone);

    // Glowing Ground Target Ring
    const ringGeo = new THREE.RingGeometry(0.8, 1.2, 24);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xFDE047, side: THREE.DoubleSide });
    this.beaconGroundRing = new THREE.Mesh(ringGeo, ringMat);
    this.beaconGroundRing.rotation.x = -Math.PI / 2;
    this.beaconGroundRing.position.y = 0.04;
    this.waypointBeacon.add(this.beaconGroundRing);

    this.scene.add(this.waypointBeacon);
    this.updateWaypointPosition();
  }

  updateWaypointPosition() {
    if (!this.waypointBeacon) return;
    const activeLevelNum = (this.player.currentLevelIndex || 0) + 1;
    const activeItem = this.interactables.find(i => i.levelNum === activeLevelNum);

    if (activeItem) {
      this.waypointBeacon.position.set(activeItem.position.x, 0, activeItem.position.z);
      this.waypointBeacon.visible = true;
    } else {
      this.waypointBeacon.visible = false;
    }
  }

  openStation(levelNum) {
    if (window.GameAudio) window.GameAudio.playClick();
    if (!window.dialogue) return;

    const activeLevelNum = (this.player.currentLevelIndex || 0) + 1;
    if (levelNum !== activeLevelNum) {
      if (levelNum < activeLevelNum) {
        this.player.showInWorldBanner(`✅ You already completed this station! Walk to Level ${activeLevelNum}.`, 'info');
      } else {
        this.player.showInWorldBanner(`🔒 This station is locked! Complete Level ${activeLevelNum} first.`, 'warning');
      }
      return;
    }

    const level = (this.player.levels || [])[levelNum - 1] || (this.player.levels || [])[0];
    const content = (level.contents || [])[0] || {};

    if (levelNum === 1) {
      window.dialogue.showSellerDialogue("Mr. Sharma", level, content);
    } else if (levelNum === 2) {
      window.dialogue.showMixerDialogue(level, content);
    } else if (levelNum === 3) {
      window.dialogue.showScannerDialogue(level, content);
    } else if (levelNum === 4) {
      window.dialogue.showMarketDialogue(level, content);
    } else if (levelNum === 5) {
      window.dialogue.showArchitectDialogue(level, content);
    }
  }

  setStage(stageNum, animate = true) {
    this.currentStage = stageNum;
    if (this.foundationMesh) this.foundationMesh.visible = stageNum >= 2;
    if (this.wallsGroup) this.wallsGroup.visible = stageNum >= 3;
    if (this.roofGroup) this.roofGroup.visible = stageNum >= 4;
    if (this.villaGroup) this.villaGroup.visible = stageNum >= 5;
    if (this.frontRibbon) this.frontRibbon.visible = stageNum === 0;
    if (this.forSaleSign) this.forSaleSign.visible = stageNum === 0;
    this.updateWaypointPosition();
  }

  onLevel1Completed() {
    this.setStage(1);
    let bzPos = 7;
    const bz = setInterval(() => {
      bzPos -= 0.18;
      this.bulldozer.position.x = bzPos;
      if (bzPos <= 1.5) {
        clearInterval(bz);
        if (this.forSaleSign) this.forSaleSign.visible = false;
        if (this.frontRibbon) this.frontRibbon.visible = false;
      }
    }, 20);

    if (window.confetti) window.confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
    this.updateWaypointPosition();
  }

  onLevel2Completed() {
    this.setStage(2);
    if (window.confetti) window.confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
    this.updateWaypointPosition();
  }

  onLevel3Completed() {
    this.setStage(3);
    if (window.confetti) window.confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
    this.updateWaypointPosition();
  }

  onLevel4Completed() {
    this.setStage(4);
    if (window.confetti) window.confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
    this.updateWaypointPosition();
  }

  onLevel5Completed() {
    this.setStage(5);
    if (window.confetti) window.confetti({ particleCount: 200, spread: 100, origin: { y: 0.5 } });
  }

  initInteractionListeners() {
    window.addEventListener('keydown', (e) => {
      if (e.key.toLowerCase() === 'e' || e.key === ' ') {
        if (this.nearbyNPC && this.nearbyNPC.onInteract) {
          this.nearbyNPC.onInteract();
        }
      }
    });

    this.container.addEventListener('click', (e) => {
      const rect = this.renderer.domElement.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, this.camera);
      const intersects = this.raycaster.intersectObjects([this.groundMesh], true);

      if (intersects.length > 0) {
        const hit = intersects[0];
        if (this.character && hit.point) {
          this.character.moveTo(hit.point);
        }
      }
    });
  }

  checkProximity() {
    if (!this.character) return;
    const charPos = this.character.position;
    const activeLevelNum = (this.player.currentLevelIndex || 0) + 1;
    let foundNearby = null;

    this.interactables.forEach(item => {
      const dist = charPos.distanceTo(item.position);
      if (dist <= item.radius) {
        foundNearby = item;
      }
    });

    this.nearbyNPC = foundNearby;
    const promptEl = document.getElementById('interaction-hud-prompt');
    if (promptEl) {
      if (this.nearbyNPC) {
        if (this.nearbyNPC.levelNum === activeLevelNum) {
          promptEl.className = 'interaction-prompt-active';
          promptEl.innerHTML = `<span class="key-badge">E</span> Interact with <strong>${this.nearbyNPC.name}</strong>`;
          promptEl.style.display = 'flex';
        } else if (this.nearbyNPC.levelNum < activeLevelNum) {
          promptEl.className = 'interaction-prompt-completed';
          promptEl.innerHTML = `<span>✅ ${this.nearbyNPC.name} (Completed)</span>`;
          promptEl.style.display = 'flex';
        } else {
          promptEl.className = 'interaction-prompt-locked';
          promptEl.innerHTML = `<span>🔒 Locked: Complete Level ${activeLevelNum} first</span>`;
          promptEl.style.display = 'flex';
        }
      } else {
        promptEl.style.display = 'none';
      }
    }
  }

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    if (this.character) {
      this.character.update();

      const targetCamX = this.character.position.x * 0.6;
      const targetCamZ = this.character.position.z + 14;
      this.camera.position.x += (targetCamX - this.camera.position.x) * 0.05;
      this.camera.position.z += (targetCamZ - this.camera.position.z) * 0.05;
      this.camera.lookAt(this.character.position.x, 1.2, this.character.position.z);
    }

    if (this.npcRightArm) {
      this.npcRightArm.rotation.z = Math.sin(Date.now() * 0.005) * 0.4 - 0.2;
    }

    // Animate Waypoint Beacon (bob up & down + pulse ring)
    if (this.waypointBeacon && this.waypointBeacon.visible) {
      this.waypointBeacon.children[0].position.y = 4.2 + Math.sin(Date.now() * 0.004) * 0.3;
      if (this.beaconGroundRing) {
        const s = 1 + Math.sin(Date.now() * 0.006) * 0.15;
        this.beaconGroundRing.scale.set(s, s, 1);
      }
    }

    this.checkProximity();
    this.renderer.render(this.scene, this.camera);
  }
}

window.House3DWorld = House3DWorld;
